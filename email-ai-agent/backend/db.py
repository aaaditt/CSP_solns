from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

import config

_engine_kwargs = {"connect_args": {"check_same_thread": False}}
if ":memory:" in config.DATABASE_URL:
    # In-memory SQLite normally gets a fresh (empty) DB per connection; StaticPool
    # forces a single shared connection so the schema created by init_db() is
    # actually visible to later queries. Used by the test suite.
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(config.DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc)


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    imap_uid = Column(String, unique=True, index=True, nullable=False)
    sender = Column(String)
    sender_email = Column(String)
    subject = Column(String)
    date = Column(DateTime)
    body_snippet = Column(String)
    is_subscription = Column(Boolean, default=False)
    category = Column(String)
    confidence = Column(Float)
    summary = Column(String)
    reviewed = Column(Boolean, default=False)
    tag = Column(String, nullable=True)
    classified_at = Column(DateTime, nullable=True)
    unsubscribe_mailto = Column(String, nullable=True)
    unsubscribe_url = Column(String, nullable=True)
    unsubscribe_one_click = Column(Boolean, default=False)
    unsubscribe_status = Column(String, nullable=True)  # None | "sent" | "failed" | "opened"
    unsubscribed_at = Column(DateTime, nullable=True)


class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=utcnow)
    finished_at = Column(DateTime, nullable=True)
    emails_fetched = Column(Integer, default=0)
    emails_classified = Column(Integer, default=0)
    status = Column(String, default="running")
    error = Column(String, nullable=True)
    trigger = Column(String, default="manual")  # "manual" | "scheduled"


class SyncCursor(Base):
    """Singleton row (id=1) tracking incremental-sync progress."""
    __tablename__ = "sync_cursor"

    id = Column(Integer, primary_key=True)
    last_uid = Column(Integer, nullable=False, default=0)
    uidvalidity = Column(String, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Setting(Base):
    """Whitelisted, non-secret runtime settings editable without a restart."""
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class ActionLog(Base):
    __tablename__ = "action_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utcnow)
    action = Column(String, nullable=False)
    email_id = Column(Integer, nullable=True)
    detail = Column(String, nullable=True)


# (table, column, sqlite DDL type + default) for columns added to tables that
# already existed before this list was introduced. create_all() only creates
# missing tables, never alters existing ones, so this covers that gap.
_NEW_COLUMNS: list[tuple[str, str, str]] = [
    ("sync_log", "trigger", "TEXT DEFAULT 'manual'"),
    ("emails", "unsubscribe_mailto", "TEXT"),
    ("emails", "unsubscribe_url", "TEXT"),
    ("emails", "unsubscribe_one_click", "BOOLEAN DEFAULT 0"),
    ("emails", "unsubscribe_status", "TEXT"),
    ("emails", "unsubscribed_at", "DATETIME"),
]


def _run_lightweight_migrations():
    with engine.connect() as conn:
        for table, column, ddl in _NEW_COLUMNS:
            cols = {row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")}
            if column not in cols:
                conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
        conn.commit()


def init_db():
    Base.metadata.create_all(bind=engine)
    _run_lightweight_migrations()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
