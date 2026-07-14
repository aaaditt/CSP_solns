"""
Whitelisted, non-secret runtime settings (sync interval, max emails per sync,
background-sync enabled) that are editable via GET/PATCH /api/settings without
restarting the process. Secrets (EMAIL_APP_PASSWORD, GOOGLE_API_KEY,
EMAIL_ADDRESS, IMAP_HOST) are never stored here or exposed through any API
response -- .env-only, permanently.

Falls back to the config.py env-var defaults until a setting is explicitly
edited, so a fresh install behaves exactly like Bundle 1's env-only version.
"""

from db import SessionLocal, Setting
import config

_DEFAULTS = {
    "sync_interval_minutes": lambda: config.SYNC_INTERVAL_MINUTES,
    "sync_max_emails": lambda: config.SYNC_MAX_EMAILS,
    "background_sync_enabled": lambda: config.BACKGROUND_SYNC_ENABLED,
}

_PARSERS = {
    "sync_interval_minutes": int,
    "sync_max_emails": int,
    "background_sync_enabled": lambda v: str(v).strip().lower() == "true",
}


def get_all() -> dict:
    db = SessionLocal()
    try:
        stored = {r.key: r.value for r in db.query(Setting).all()}
        return {
            key: _PARSERS[key](stored[key]) if key in stored else default()
            for key, default in _DEFAULTS.items()
        }
    finally:
        db.close()


def get(key: str):
    return get_all()[key]


def set_many(values: dict) -> dict:
    db = SessionLocal()
    try:
        for key, value in values.items():
            if key not in _DEFAULTS:
                continue
            row = db.query(Setting).filter(Setting.key == key).first()
            if row is None:
                db.add(Setting(key=key, value=str(value)))
            else:
                row.value = str(value)
        db.commit()
    finally:
        db.close()
    return get_all()
