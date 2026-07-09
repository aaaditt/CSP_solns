from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///emails.db", connect_args={"check_same_thread": False})
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


class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=utcnow)
    finished_at = Column(DateTime, nullable=True)
    emails_fetched = Column(Integer, default=0)
    emails_classified = Column(Integer, default=0)
    status = Column(String, default="running")
    error = Column(String, nullable=True)


class ActionLog(Base):
    __tablename__ = "action_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utcnow)
    action = Column(String, nullable=False)
    email_id = Column(Integer, nullable=True)
    detail = Column(String, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
