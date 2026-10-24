from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    gmail_message_id: str
    sender: str
    subject: str
    received_at: datetime | None
    summary: str | None
    language: str
    status: str
    created_at: datetime


class IngestResult(BaseModel):
    fetched: int
    ingested: int
    skipped_duplicates: int
