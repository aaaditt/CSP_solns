"""
Background sync scheduler.

Runs agent.run_sync() on an interval so the user never has to click "Sync"
for new mail to show up. Leader election uses a cross-process file lock
rather than any assumption about uvicorn --reload's process layout --
whichever process grabs the lock owns the schedule; the OS releases the lock
automatically when that process exits, so a reload (old worker killed, new
one started) hands leadership over cleanly with no stale-lock cleanup needed.

This process always claims leadership at startup (if available), independent
of whether background sync is currently enabled -- that way, if the user
later flips background_sync_enabled on via the settings panel, a leader is
already in place ready to add the job, rather than requiring a restart.
"""

from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from filelock import FileLock, Timeout

import agent
import settings_store

_JOB_ID = "background_sync"
_LOCK_PATH = Path(__file__).parent / ".scheduler.lock"
_lock = FileLock(str(_LOCK_PATH), timeout=0)
_scheduler = BackgroundScheduler()
_is_leader = False


def start() -> bool:
    """Claims leadership and applies current settings. Returns True if this process is now the leader."""
    global _is_leader

    try:
        _lock.acquire(timeout=0)
    except Timeout:
        return False  # another process is already the scheduler leader

    _is_leader = True
    _scheduler.start()
    apply_settings()
    return True


def apply_settings() -> bool:
    """
    Adds/removes/reschedules the background job to match current settings
    (settings_store, which falls back to config.py env defaults). Call after
    startup and after any PATCH /api/settings change. Returns False if this
    process isn't the leader (nothing to do).
    """
    if not _is_leader:
        return False

    settings = settings_store.get_all()
    existing = _scheduler.get_job(_JOB_ID)

    if not settings["background_sync_enabled"]:
        if existing:
            _scheduler.remove_job(_JOB_ID)
        return True

    if existing is None:
        _scheduler.add_job(
            agent.run_sync, "interval", minutes=settings["sync_interval_minutes"],
            id=_JOB_ID, max_instances=1, coalesce=True,
            kwargs={"trigger": "scheduled"},
        )
    else:
        _scheduler.reschedule_job(_JOB_ID, trigger="interval", minutes=settings["sync_interval_minutes"])
    return True


def stop() -> None:
    global _is_leader
    if _is_leader:
        _scheduler.shutdown(wait=False)
        _lock.release()
        _is_leader = False
