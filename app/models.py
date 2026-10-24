from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.db import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    gmail_message_id = Column(String(64), unique=True, nullable=False, index=True)
    sender = Column(String(320), nullable=False)
    subject = Column(String(998), nullable=False)
    received_at = Column(DateTime, nullable=True)
    raw_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    language = Column(String(32), nullable=False, default="English")
    status = Column(String(32), nullable=False, default="new")
    created_at = Column(DateTime, server_default=func.now())
