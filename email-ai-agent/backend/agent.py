"""
Sync orchestration: fetch new mail -> classify -> persist.

Kept separate from main.py so the sync logic can be invoked identically from
the API route, the background scheduler, or a test script.
"""

import threading

from db import SessionLocal, Email, SyncLog, SyncCursor, ActionLog, utcnow
import mail_client
import classifier
import settings_store

# Serializes manual (button-click) and scheduled runs within this process --
# APScheduler's max_instances=1 only protects against overlapping scheduled
# runs, not a manual sync landing mid-scheduled-run.
_sync_lock = threading.Lock()


def _get_or_create_cursor(db) -> SyncCursor:
    cursor = db.query(SyncCursor).filter(SyncCursor.id == 1).first()
    if cursor is None:
        # First run after the cursor feature ships: if emails already exist
        # (synced by the old count-based fetch_recent()), start at the
        # highest UID already seen instead of 0, so we don't re-crawl the
        # entire mailbox history from the beginning.
        existing_uids = [int(row[0]) for row in db.query(Email.imap_uid).all()]
        cursor = SyncCursor(id=1, last_uid=max(existing_uids, default=0))
        db.add(cursor)
        db.commit()
        db.refresh(cursor)
    return cursor


def run_sync(trigger: str = "manual") -> dict:
    if not _sync_lock.acquire(blocking=False):
        return {"fetched": 0, "classified": 0, "skipped": 0, "status": "skipped",
                "error": "a sync is already running"}

    try:
        db = SessionLocal()
        sync_log = SyncLog(status="running", trigger=trigger)
        db.add(sync_log)
        db.commit()
        db.refresh(sync_log)

        fetched = 0
        classified = 0
        skipped = 0

        try:
            cursor = _get_or_create_cursor(db)

            current_uidvalidity = mail_client.get_uidvalidity()
            if cursor.uidvalidity and cursor.uidvalidity != current_uidvalidity:
                cursor.last_uid = 0  # mailbox was recreated; UIDs are meaningless now
            cursor.uidvalidity = current_uidvalidity

            max_emails = settings_store.get("sync_max_emails")
            emails, _more_available = mail_client.fetch_since(cursor.last_uid, max_emails)
            fetched = len(emails)

            existing_uids = {row[0] for row in db.query(Email.imap_uid).all()}

            for e in emails:
                uid_int = int(e["imap_uid"])

                if e["imap_uid"] in existing_uids:
                    skipped += 1
                    cursor.last_uid = max(cursor.last_uid, uid_int)
                    continue

                result = classifier.classify_email(
                    sender=e["sender"],
                    sender_email=e["sender_email"],
                    subject=e["subject"],
                    body_snippet=e["body_snippet"],
                )

                db.add(Email(
                    imap_uid=e["imap_uid"],
                    sender=e["sender"],
                    sender_email=e["sender_email"],
                    subject=e["subject"],
                    date=e["date"],
                    body_snippet=e["body_snippet"],
                    is_subscription=result["is_subscription"],
                    category=result["category"],
                    confidence=result["confidence"],
                    summary=result["summary"],
                    classified_at=utcnow(),
                    unsubscribe_mailto=e.get("unsubscribe_mailto"),
                    unsubscribe_url=e.get("unsubscribe_url"),
                    unsubscribe_one_click=e.get("unsubscribe_one_click", False),
                ))
                classified += 1
                # Advance as each email is actually queued for persistence, not
                # just once at the end -- if a later email in this batch raises,
                # the finally-block commit below still only commits emails added
                # so far, and the cursor stays consistent with what was saved.
                cursor.last_uid = max(cursor.last_uid, uid_int)

            db.add(cursor)
            sync_log.status = "success"
        except Exception as exc:
            sync_log.status = "failed"
            sync_log.error = str(exc)
        finally:
            sync_log.finished_at = utcnow()
            sync_log.emails_fetched = fetched
            sync_log.emails_classified = classified
            db.add(ActionLog(
                action="sync",
                detail=f"trigger={trigger} fetched={fetched} classified={classified} skipped={skipped}",
            ))
            db.commit()
            status = sync_log.status
            error = sync_log.error
            db.close()

        return {"fetched": fetched, "classified": classified, "skipped": skipped, "status": status, "error": error}
    finally:
        _sync_lock.release()
