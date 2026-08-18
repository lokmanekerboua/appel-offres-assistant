import logging
import time

from openai import OpenAI, APIError, RateLimitError, APIStatusError

from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)


def call_groq(messages: list[dict], tools: list[dict] | None = None) -> object:
    """
    Wrapper around Groq's chat completion API (OpenAI-compatible).
    """
    max_retries = 3
    backoff_seconds = 2

    for attempt in range(1, max_retries + 1):
        start = time.monotonic()
        try:
            response = client.chat.completions.create(
                model=settings.model_name,
                max_tokens=settings.max_tokens,
                messages=messages,
                tools=tools or None,
            )
            elapsed = time.monotonic() - start
            logger.info(
                "groq_call_success",
                extra={
                    "attempt": attempt,
                    "elapsed_seconds": round(elapsed, 2),
                    "finish_reason": response.choices[0].finish_reason,
                },
            )
            return response

        except RateLimitError:
            logger.warning(f"rate_limited, retrying in {backoff_seconds}s (attempt {attempt})")
            time.sleep(backoff_seconds)
            backoff_seconds *= 2

        except APIStatusError as e:
            logger.error(f"groq_api_status_error: {e.status_code} - {e.message}")
            if attempt == max_retries:
                raise
            time.sleep(backoff_seconds)

        except APIError as e:
            logger.error(f"groq_api_error: {e}")
            raise

    raise RuntimeError("Groq call failed after max retries")