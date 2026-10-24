from anthropic import Anthropic

from app.config import settings

_client = Anthropic(api_key=settings.anthropic_api_key)

PROMPT = """Summarize the following article in 3-5 concise sentences, written in {language}. \
Return only the summary, with no preamble.

---
{text}
"""


def summarize_and_translate(text: str, language: str | None = None) -> str:
    language = language or settings.target_language
    response = _client.messages.create(
        model=settings.anthropic_model,
        max_tokens=512,
        messages=[{"role": "user", "content": PROMPT.format(language=language, text=text[:12000])}],
    )
    return response.content[0].text.strip()
