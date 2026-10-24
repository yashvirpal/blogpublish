# blogpublish

Reads articles out of a Gmail inbox, summarizes + translates each one to
English with the Claude API, and stores the result in Postgres so it's ready
to publish from.

## How it works

1. `POST /ingest` lists Gmail messages matching `GMAIL_QUERY` (default:
   `in:inbox is:unread`), skipping any `gmail_message_id` already stored.
2. Each new message's body is extracted (plain text, or HTML stripped to
   text) and sent to Claude for a short summary in `TARGET_LANGUAGE`.
3. The original text + summary are saved as an `Article` row with
   `status=summarized`.
4. If `GMAIL_MARK_AS_READ=true`, the Gmail message has its `UNREAD` label
   removed after it's stored.
5. `GET /articles` / `GET /articles/{id}` list what's ready to publish.

Publishing the summarized articles to reativecoders.com is a separate step
once that site's API/credentials are available — `status` is there so a
future `/publish` endpoint can flip rows to `published`.

## Setup

### 1. Database

This reuses the shared Postgres from `yp/database` (the `db-network` stack)
instead of running its own. Make sure that stack is up:

```bash
cd ../database
docker compose up -d
```

### 2. Gmail API credentials

1. In Google Cloud Console, create an OAuth client ID of type **Desktop app**
   and download it.
2. Save it as `credentials/credentials.json` in this project.
3. On first `/ingest` call, a browser window opens for you to grant Gmail
   access; the resulting token is cached at `credentials/token.json` so you
   won't be prompted again.

### 3. Environment

```bash
cp .env.example .env
```

Fill in `DATABASE_URL` (point it at `db-postgres`'s credentials) and
`ANTHROPIC_API_KEY`.

### 4. Run

Locally:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Or in Docker (attaches to `db-network`, so the shared stack must be running
first):

```bash
docker compose up --build
```

### 5. Use it

```bash
curl -X POST http://localhost:8000/ingest
curl http://localhost:8000/articles
```
