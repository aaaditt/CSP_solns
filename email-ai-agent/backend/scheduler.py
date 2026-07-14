"""
Background sync scheduler.

Runs agent.run_sync() on a fixed interval so the user never has to click
"Sync" for new mail to show up. Leader election uses a cross-process file
lock rather than any assumption about uvicorn --reload's process layout --
whichever process grabs the lock owns the schedule; the OS releases the lock
automatically when that process exits, so a reload (old worker killed, new
one started) hands leadership over cleanly with no stale-lock cleanup needed.
"""

from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from filelock import FileLock, Timeout

import agent
import config

_LOCK_PATH = Path(__file__).parent / ".scheduler.lock"
_lock = FileLock(str(_LOCK_PATH), timeout=0)
_scheduler = BackgroundScheduler()
_is_leader = False


def start() -> bool:
    """Starts the background sync job if enabled and this process wins the leader lock."""
    global _is_leader

    if not config.BACKGROUND_SYNC_ENABLED:
        return False

    try:
        _lock.acquire(timeout=0)
    except Timeout:
        return False  # another process is already the scheduler leader

    _is_leader = True
    _scheduler.add_job(
        agent.run_sync,
        "interval",
        minutes=config.SYNC_INTERVAL_MINUTES,
        id="background_sync",
        max_instances=1,
        coalesce=True,
        kwargs={"trigger": "scheduled"},
    )
    _scheduler.start()
    return True


def reschedule(interval_minutes: int) -> bool:
    """Updates the running job's interval live. Returns False if this process isn't the leader."""
    if not _is_leader:
        return False
    _scheduler.reschedule_job("background_sync", trigger="interval", minutes=interval_minutes)
    return True


def stop() -> None:
    global _is_leader
    if _is_leader:
        _scheduler.shutdown(wait=False)
        _lock.release()
        _is_leader = False
