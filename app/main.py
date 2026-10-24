from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, SessionLocal, engine, get_db
from app.gmail_ingest.client import get_gmail_service, get_message, list_message_ids, mark_as_read
from app.gmail_ingest.extractor import extract_article
from app.models import Article
from app.schemas import ArticleOut, IngestResult
from app.summarize import summarize_and_translate

app = FastAPI(title="blogpublish")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResult)
def ingest() -> IngestResult:
    service = get_gmail_service()
    message_ids = list_message_ids(service, settings.gmail_query)

    ingested = 0
    skipped = 0
    db: Session = SessionLocal()
    try:
        for message_id in message_ids:
            if db.query(Article).filter_by(gmail_message_id=message_id).first():
                skipped += 1
                continue

            message = get_message(service, message_id)
            article_data = extract_article(message)
            summary = summarize_and_translate(article_data["raw_text"])

            db.add(
                Article(
                    **article_data,
                    summary=summary,
                    language=settings.target_language,
                    status="summarized",
                )
            )
            db.commit()
            ingested += 1

            if settings.gmail_mark_as_read:
                mark_as_read(service, message_id)
    finally:
        db.close()

    return IngestResult(fetched=len(message_ids), ingested=ingested, skipped_duplicates=skipped)


@app.get("/articles", response_model=list[ArticleOut])
def list_articles(status: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Article)
    if status:
        query = query.filter_by(status=status)
    return query.order_by(Article.created_at.desc()).limit(limit).all()


@app.get("/articles/{article_id}", response_model=ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
