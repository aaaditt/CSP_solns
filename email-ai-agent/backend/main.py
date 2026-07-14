import csv
import io
import ipaddress
import socket
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from db import init_db, get_db, utcnow, Email, SyncLog, ActionLog
import agent
import mail_client
import scheduler
import settings_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="Email AI Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_email_query(
    db: Session,
    subscription_only: bool = True,
    category: str | None = None,
    reviewed: bool | None = None,
    search: str | None = None,
    sort: str = "date_desc",
    ids: list[int] | None = None,
):
    """Shared filter logic for GET /api/emails and GET /api/export."""
    query = db.query(Email)

    if ids is not None:
        # "Export just what I selected" -- overrides the normal filter set.
        query = query.filter(Email.id.in_(ids))
    else:
        if subscription_only:
            query = query.filter(Email.is_subscription == True)  # noqa: E712
        if category:
            query = query.filter(Email.category == category)
        if reviewed is not None:
            query = query.filter(Email.reviewed == reviewed)
        if search:
            like = f"%{search}%"
            query = query.filter(or_(Email.sender.ilike(like), Email.subject.ilike(like)))

    if sort == "date_asc":
        query = query.order_by(Email.date.asc())
    else:
        query = query.order_by(Email.date.desc())

    return query


@app.post("/api/sync")
def sync():
    return agent.run_sync(trigger="manual")


@app.get("/api/emails")
def list_emails(
    subscription_only: bool = True,
    category: str | None = None,
    reviewed: bool | None = None,
    search: str | None = None,
    sort: str = "date_desc",
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = build_email_query(db, subscription_only, category, reviewed, search, sort)
    total = query.count()
    rows = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "emails": [_email_dict(r) for r in rows],
    }


def _email_dict(r: Email) -> dict:
    return {
        "id": r.id,
        "sender": r.sender,
        "sender_email": r.sender_email,
        "subject": r.subject,
        "date": r.date,
        "body_snippet": r.body_snippet,
        "is_subscription": r.is_subscription,
        "category": r.category,
        "confidence": r.confidence,
        "summary": r.summary,
        "reviewed": r.reviewed,
        "tag": r.tag,
        "unsubscribe_mailto": r.unsubscribe_mailto,
        "unsubscribe_url": r.unsubscribe_url,
        "unsubscribe_one_click": r.unsubscribe_one_click,
        "unsubscribe_status": r.unsubscribe_status,
        "unsubscribed_at": r.unsubscribed_at,
    }


@app.get("/api/emails/{email_id}")
def get_email(email_id: int, db: Session = Depends(get_db)):
    row = db.query(Email).filter(Email.id == email_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Email not found")

    result = _email_dict(row)
    try:
        result["full_body"] = mail_client.fetch_full_body(row.imap_uid)
        result["error"] = None
    except Exception as exc:
        result["full_body"] = None
        result["error"] = str(exc)

    db.add(ActionLog(action="open_email", email_id=email_id))
    db.commit()
    return result


class BulkEmailPatch(BaseModel):
    ids: list[int]
    reviewed: bool | None = None
    tag: str | None = None


@app.patch("/api/emails/bulk")
def patch_emails_bulk(patch: BulkEmailPatch, db: Session = Depends(get_db)):
    # Registered before /api/emails/{email_id} so "bulk" is never swallowed
    # by the {email_id}: int path parameter.
    if not patch.ids:
        return {"updated": 0}

    rows = db.query(Email).filter(Email.id.in_(patch.ids)).all()
    changes = []
    for row in rows:
        if patch.reviewed is not None:
            row.reviewed = patch.reviewed
        if patch.tag is not None:
            row.tag = patch.tag
    if patch.reviewed is not None:
        changes.append(f"reviewed={patch.reviewed}")
    if patch.tag is not None:
        changes.append(f"tag={patch.tag}")

    db.add(ActionLog(action="bulk_update", detail=f"{len(rows)} emails: {', '.join(changes)}"))
    db.commit()
    return {"updated": len(rows)}


class EmailPatch(BaseModel):
    reviewed: bool | None = None
    tag: str | None = None
    unsubscribe_status: str | None = None


@app.patch("/api/emails/{email_id}")
def patch_email(email_id: int, patch: EmailPatch, db: Session = Depends(get_db)):
    row = db.query(Email).filter(Email.id == email_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Email not found")

    if patch.reviewed is not None:
        row.reviewed = patch.reviewed
        db.add(ActionLog(action="mark_reviewed", email_id=email_id, detail=str(patch.reviewed)))
    if patch.tag is not None:
        row.tag = patch.tag
        db.add(ActionLog(action="tag", email_id=email_id, detail=patch.tag))
    if patch.unsubscribe_status is not None:
        # Clients may only self-report having opened the link/mailto -- "sent"
        # is exclusively set server-side by POST .../unsubscribe after an
        # actual one-click request succeeds, so a client can't spoof success.
        if patch.unsubscribe_status != "opened":
            raise HTTPException(
                status_code=400,
                detail="unsubscribe_status can only be set to 'opened' via this endpoint",
            )
        row.unsubscribe_status = "opened"
        db.add(ActionLog(action="unsubscribe_opened", email_id=email_id))

    db.commit()
    db.refresh(row)
    return _email_dict(row)


def _is_safe_unsubscribe_url(url: str) -> bool:
    """
    SSRF guard: unsubscribe_url comes from parsing an untrusted email's
    List-Unsubscribe header, so before the backend ever POSTs to it
    server-side (the one-click path), reject anything that isn't a plain
    http(s) URL resolving to a public address -- otherwise a crafted email
    could make this server hit internal services or cloud metadata endpoints
    (e.g. 169.254.169.254) just by having the user click Unsubscribe.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.hostname or parsed.username or parsed.password:
        return False

    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        return False

    return all(
        not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)
        for ip in (ipaddress.ip_address(info[4][0]) for info in infos)
    )


@app.post("/api/emails/{email_id}/unsubscribe")
def unsubscribe_email(email_id: int, db: Session = Depends(get_db)):
    """
    Safety model: only the RFC 8058 "one-click" contract (List-Unsubscribe-Post:
    List-Unsubscribe=One-Click plus an https List-Unsubscribe link) is ever
    fetched server-side -- that contract is specifically designed to be
    automatable (no confirmation page, idempotent; mail clients like Gmail
    already do this without asking). A bare link or mailto is handed back
    untouched for the frontend to open -- the backend never makes an outbound
    request for those, since a plain GET can be a tracking pixel or gate the
    real unsubscribe action behind a confirmation page.
    """
    row = db.query(Email).filter(Email.id == email_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Email not found")

    if row.unsubscribe_one_click and row.unsubscribe_url:
        if not _is_safe_unsubscribe_url(row.unsubscribe_url):
            row.unsubscribe_status = "failed"
            db.add(ActionLog(action="unsubscribe", email_id=email_id, detail="blocked: unsafe unsubscribe URL"))
            db.commit()
            return {
                "action": "completed", "url": None, "mailto": None,
                "status": "failed", "detail": "unsubscribe URL failed a safety check",
            }

        try:
            resp = httpx.post(
                row.unsubscribe_url,
                data={"List-Unsubscribe": "One-Click"},
                timeout=10.0,
                follow_redirects=False,  # don't blindly follow a redirect into an internal address
            )
            success = resp.status_code < 400
            detail = f"HTTP {resp.status_code}"
        except httpx.HTTPError as exc:
            success = False
            detail = str(exc)

        row.unsubscribe_status = "sent" if success else "failed"
        row.unsubscribed_at = utcnow() if success else None
        db.add(ActionLog(
            action="unsubscribe",
            email_id=email_id,
            detail=f"one_click status={row.unsubscribe_status} ({detail})",
        ))
        db.commit()
        return {"action": "completed", "url": None, "mailto": None, "status": row.unsubscribe_status, "detail": detail}

    if row.unsubscribe_url:
        db.add(ActionLog(action="unsubscribe", email_id=email_id, detail="handed link to client"))
        db.commit()
        return {"action": "open_link", "url": row.unsubscribe_url, "mailto": None, "status": None, "detail": None}

    if row.unsubscribe_mailto:
        db.add(ActionLog(action="unsubscribe", email_id=email_id, detail="handed mailto to client"))
        db.commit()
        return {"action": "open_mailto", "url": None, "mailto": row.unsubscribe_mailto, "status": None, "detail": None}

    raise HTTPException(status_code=400, detail="No unsubscribe method found for this email")


@app.get("/api/export")
def export_csv(
    subscription_only: bool = True,
    category: str | None = None,
    reviewed: bool | None = None,
    search: str | None = None,
    sort: str = "date_desc",
    ids: str | None = None,  # comma-separated email ids -- "export just what I selected"
    db: Session = Depends(get_db),
):
    id_list = [int(x) for x in ids.split(",") if x.strip()] if ids else None
    query = build_email_query(db, subscription_only, category, reviewed, search, sort, ids=id_list)
    rows = query.all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "sender", "sender_email", "subject", "date", "category", "confidence", "summary", "reviewed", "tag"])
    for r in rows:
        writer.writerow([r.id, r.sender, r.sender_email, r.subject, r.date, r.category, r.confidence, r.summary, r.reviewed, r.tag])

    db.add(ActionLog(action="export", detail=f"{len(rows)} rows"))
    db.commit()

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=emails_export.csv"},
    )


@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Email.id)).filter(Email.is_subscription == True).scalar()  # noqa: E712
    unreviewed = db.query(func.count(Email.id)).filter(Email.is_subscription == True, Email.reviewed == False).scalar()  # noqa: E712

    by_category = dict(
        db.query(Email.category, func.count(Email.id))
        .filter(Email.is_subscription == True)  # noqa: E712
        .group_by(Email.category)
        .all()
    )

    last_sync = db.query(SyncLog).order_by(SyncLog.started_at.desc()).first()

    return {
        "total_subscriptions": total,
        "unreviewed": unreviewed,
        "by_category": by_category,
        "last_sync": None if last_sync is None else {
            "started_at": last_sync.started_at,
            "finished_at": last_sync.finished_at,
            "emails_fetched": last_sync.emails_fetched,
            "emails_classified": last_sync.emails_classified,
            "status": last_sync.status,
            "error": last_sync.error,
            "trigger": last_sync.trigger,
        },
    }


class SettingsPatch(BaseModel):
    sync_interval_minutes: int | None = None
    sync_max_emails: int | None = None
    background_sync_enabled: bool | None = None


@app.get("/api/settings")
def get_settings():
    return settings_store.get_all()


@app.patch("/api/settings")
def patch_settings(patch: SettingsPatch):
    updates = {}
    if patch.sync_interval_minutes is not None:
        if not (5 <= patch.sync_interval_minutes <= 1440):
            raise HTTPException(status_code=400, detail="sync_interval_minutes must be between 5 and 1440")
        updates["sync_interval_minutes"] = patch.sync_interval_minutes
    if patch.sync_max_emails is not None:
        if not (1 <= patch.sync_max_emails <= 100):
            raise HTTPException(status_code=400, detail="sync_max_emails must be between 1 and 100")
        updates["sync_max_emails"] = patch.sync_max_emails
    if patch.background_sync_enabled is not None:
        updates["background_sync_enabled"] = patch.background_sync_enabled

    result = settings_store.set_many(updates)
    scheduler.apply_settings()  # live: no restart needed for interval/enabled changes
    return result
