import csv
import io
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from db import init_db, get_db, Email, SyncLog, ActionLog
import agent
import mail_client
import scheduler


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
):
    """Shared filter logic for GET /api/emails and GET /api/export."""
    query = db.query(Email)

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
        "emails": [
            {
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
            }
            for r in rows
        ],
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


class EmailPatch(BaseModel):
    reviewed: bool | None = None
    tag: str | None = None


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

    db.commit()
    db.refresh(row)
    return _email_dict(row)


@app.get("/api/export")
def export_csv(
    subscription_only: bool = True,
    category: str | None = None,
    reviewed: bool | None = None,
    search: str | None = None,
    sort: str = "date_desc",
    db: Session = Depends(get_db),
):
    query = build_email_query(db, subscription_only, category, reviewed, search, sort)
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
