import logging
import time

from anthropic import Anthropic, APIError, APIStatusError, RateLimitError

from app.core.config import settings

logger = logging.getLogger(__name__)

client = Anthropic(api_key=settings.anthropic_api_key)


def call_claude(messages: list[dict], tools: list[dict] | None = None, system: str = "") -> object:
    """
    Wrapper around the Anthropic API call with basic retry handling.
    Keeps error handling / latency logging in one place instead of
    duplicating it inside every tool or the orchestrator.
    """
    max_retries = 3
    backoff_seconds = 2

    for attempt in range(1, max_retries + 1):
        start = time.monotonic()
        try:
            response = client.messages.create(
                model=settings.model_name,
                max_tokens=settings.max_tokens,
                system=system,
                messages=messages,
                tools=tools or [],
            )
            elapsed = time.monotonic() - start
            logger.info(
                "claude_call_success",
                extra={
                    "attempt": attempt,
                    "elapsed_seconds": round(elapsed, 2),
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "stop_reason": response.stop_reason,
                },
            )
            return response

        except RateLimitError:
            logger.warning(f"rate_limited, retrying in {backoff_seconds}s (attempt {attempt})")
            time.sleep(backoff_seconds)
            backoff_seconds *= 2

        except APIStatusError as e:
            logger.error(f"claude_api_status_error: {e.status_code} - {e.message}")
            if attempt == max_retries:
                raise
            time.sleep(backoff_seconds)

        except APIError as e:
            logger.error(f"claude_api_error: {e}")
            raise

    raise RuntimeError("Claude call failed after max retries")