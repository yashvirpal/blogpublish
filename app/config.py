from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:changeme@localhost:5432/app"

    gmail_credentials_file: str = "credentials/credentials.json"
    gmail_token_file: str = "credentials/token.json"
    gmail_query: str = "in:inbox is:unread"
    gmail_mark_as_read: bool = True

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5-5"
    target_language: str = "English"

    class Config:
        env_file = ".env"


settings = Settings()
