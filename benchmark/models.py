"""Model API wrappers for the AI Brainteaser Benchmark."""

import asyncio
import os
import logging
from dataclasses import dataclass

import openai
import anthropic
from google import genai

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
RETRY_BASE_DELAY = 2  # seconds


@dataclass
class ModelConfig:
    name: str
    provider: str
    model_id: str
    enabled: bool = True
    base_url: str | None = None
    api_key_env: str | None = None
    reasoning_effort: str | None = None
    max_tokens: int | None = None


@dataclass
class ModelResponse:
    model_name: str
    question_id: int
    run_number: int
    response_text: str
    input_tokens: int
    output_tokens: int
    error: str | None = None


def _is_retryable(e: Exception) -> bool:
    """Check if an error is transient and worth retrying."""
    # OpenAI
    if isinstance(e, openai.RateLimitError):
        return True
    if isinstance(e, openai.APIStatusError) and e.status_code in (429, 500, 502, 503, 529):
        return True
    # Anthropic
    if isinstance(e, anthropic.RateLimitError):
        return True
    if isinstance(e, anthropic.APIStatusError) and e.status_code in (429, 500, 502, 503, 529):
        return True
    # Generic connection errors
    if isinstance(e, (ConnectionError, TimeoutError, asyncio.TimeoutError)):
        return True
    msg = str(e).lower()
    if "overloaded" in msg or "rate" in msg or "capacity" in msg:
        return True
    return False


def _get_openai_client(config: ModelConfig) -> openai.AsyncOpenAI:
    if config.provider == "openai_compatible":
        api_key = os.environ.get(config.api_key_env or "", "")
        return openai.AsyncOpenAI(base_url=config.base_url, api_key=api_key)
    return openai.AsyncOpenAI()


def _get_anthropic_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic()


def _get_google_client() -> genai.Client:
    return genai.Client()


async def query_model(
    config: ModelConfig,
    question: str,
    question_id: int,
    run_number: int,
    max_tokens: int = 512,
) -> ModelResponse:
    """Send a question to a model with exponential backoff retry."""
    effective_max_tokens = config.max_tokens or max_tokens
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            if config.provider in ("openai", "openai_compatible"):
                return await _query_openai(config, question, question_id, run_number, effective_max_tokens)
            elif config.provider == "anthropic":
                return await _query_anthropic(config, question, question_id, run_number, effective_max_tokens)
            elif config.provider == "google":
                return await _query_google(config, question, question_id, run_number, effective_max_tokens)
            else:
                raise ValueError(f"Unknown provider: {config.provider}")
        except Exception as e:
            last_error = e
            if _is_retryable(e) and attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning(
                    f"Retryable error for {config.name} (q{question_id}, run{run_number}), "
                    f"attempt {attempt + 1}/{MAX_RETRIES}, retrying in {delay}s: {e}"
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"Error querying {config.name} (q{question_id}, run{run_number}): {e}")
                return ModelResponse(
                    model_name=config.name,
                    question_id=question_id,
                    run_number=run_number,
                    response_text="",
                    input_tokens=0,
                    output_tokens=0,
                    error=str(e),
                )

    # Should not reach here, but just in case
    return ModelResponse(
        model_name=config.name,
        question_id=question_id,
        run_number=run_number,
        response_text="",
        input_tokens=0,
        output_tokens=0,
        error=str(last_error),
    )


async def _query_openai(
    config: ModelConfig,
    question: str,
    question_id: int,
    run_number: int,
    max_tokens: int,
) -> ModelResponse:
    client = _get_openai_client(config)
    # Newer OpenAI models (o-series, gpt-5+) require max_completion_tokens
    uses_new_api = any(config.model_id.startswith(p) for p in ("o1", "o3", "o4", "gpt-5"))
    kwargs: dict = {
        "model": config.model_id,
        "messages": [{"role": "user", "content": question}],
    }
    if uses_new_api:
        kwargs["max_completion_tokens"] = max_tokens
    else:
        kwargs["max_tokens"] = max_tokens
    if config.reasoning_effort:
        kwargs["reasoning_effort"] = config.reasoning_effort
    resp = await client.chat.completions.create(**kwargs)
    choice = resp.choices[0]
    usage = resp.usage or openai.types.CompletionUsage(
        prompt_tokens=0, completion_tokens=0, total_tokens=0
    )
    return ModelResponse(
        model_name=config.name,
        question_id=question_id,
        run_number=run_number,
        response_text=choice.message.content or "",
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
    )


async def _query_anthropic(
    config: ModelConfig,
    question: str,
    question_id: int,
    run_number: int,
    max_tokens: int,
) -> ModelResponse:
    client = _get_anthropic_client()
    kwargs: dict = {
        "model": config.model_id,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": question}],
    }
    # Anthropic extended thinking (adaptive mode)
    if config.reasoning_effort:
        kwargs["thinking"] = {"type": "adaptive"}
    resp = await client.messages.create(**kwargs)
    text = "".join(block.text for block in resp.content if block.type == "text")
    return ModelResponse(
        model_name=config.name,
        question_id=question_id,
        run_number=run_number,
        response_text=text,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
    )


async def _query_google(
    config: ModelConfig,
    question: str,
    question_id: int,
    run_number: int,
    max_tokens: int,
) -> ModelResponse:
    client = _get_google_client()
    resp = await client.aio.models.generate_content(
        model=config.model_id,
        contents=question,
        config=genai.types.GenerateContentConfig(max_output_tokens=max_tokens),
    )
    text = resp.text or ""
    usage_meta = resp.usage_metadata
    return ModelResponse(
        model_name=config.name,
        question_id=question_id,
        run_number=run_number,
        response_text=text,
        input_tokens=getattr(usage_meta, "prompt_token_count", 0) or 0,
        output_tokens=getattr(usage_meta, "candidates_token_count", 0) or 0,
    )
