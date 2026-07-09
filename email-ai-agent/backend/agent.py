"""
Sync orchestration: fetch new mail -> classify -> persist.

Kept separate from main.py so the sync logic can be invoked identically from
the API route, a future CLI/cron entrypoint, or a test script.
"""

from db import SessionLocal, Email, SyncLog, ActionLog, utcnow
import mail_client
import classifier
import config


def run_sync() -> dict:
    db = SessionLocal()
    sync_log = SyncLog(status="running")
    db.add(sync_log)
    db.commit()
    db.refresh(sync_log)

    fetched = 0
    classified = 0
    skipped = 0

    try:
        emails = mail_client.fetch_recent(config.SYNC_MAX_EMAILS)
        fetched = len(emails)

        existing_uids = {row[0] for row in db.query(Email.imap_uid).all()}

        for e in emails:
            if e["imap_uid"] in existing_uids:
                skipped += 1
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
            ))
            classified += 1

        sync_log.status = "success"
    except Exception as exc:
        sync_log.status = "failed"
        sync_log.error = str(exc)
    finally:
        sync_log.finished_at = utcnow()
        sync_log.emails_fetched = fetched
        sync_log.emails_classified = classified
        db.add(ActionLog(action="sync", detail=f"fetched={fetched} classified={classified} skipped={skipped}"))
        db.commit()
        status = sync_log.status
        error = sync_log.error
        db.close()

    return {"fetched": fetched, "classified": classified, "skipped": skipped, "status": status, "error": error}
