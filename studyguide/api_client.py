"""Asynchronous API client for interacting with the Perplexity API."""

import httpx
import structlog
from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from studyguide.config import settings

# Configure logger for this module
log = structlog.get_logger()

# --- Cache Configuration ---
# Configure cache based on settings (defaults to in-memory)
# Designed to be easily swappable to Redis by changing config
cache_config = {
    "cache": Cache.MEMORY if settings.app.cache_type == "memory" else Cache.REDIS,
    "serializer": JsonSerializer(),
    "namespace": "perplexity_api",
    "ttl": 3600, # Default TTL: 1 hour
}
if settings.app.cache_type == "redis" and settings.app.redis_url:
    cache_config["endpoint"] = settings.app.redis_url.split(":")[1].replace("//", "")
    cache_config["port"] = settings.app.redis_url.split(":")[2].split("/")[0]
    # Add password, db number if needed from URL parsing
    log.info("Using Redis cache backend", endpoint=cache_config["endpoint"], port=cache_config["port"])
else:
    log.info("Using in-memory cache backend")

# --- HTTP Client Configuration ---
# Create a single, shared AsyncClient instance for connection pooling
# Timeout configuration: 5s connect, 60s read
_client_timeout = httpx.Timeout(5.0, read=60.0)
# Follow redirects, use HTTP/2 if available
async_client = httpx.AsyncClient(
    base_url="https://api.perplexity.ai", # TODO: Potentially make configurable
    headers={
        "Authorization": f"Bearer {settings.api.api_key.get_secret_value()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    },
    timeout=_client_timeout,
    http2=True,
    follow_redirects=True,
)

# --- Retry Configuration ---
# Retry on common transient HTTP errors and timeouts
# Exponential backoff: 2s -> 4s -> 8s -> ... up to 60s max wait
retry_config = {
    "stop": stop_after_attempt(5),
    "wait": wait_exponential(multiplier=1, min=2, max=60),
    "retry": retry_if_exception_type(
        (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.HTTPStatusError, # Retry on 5xx errors specifically?
            # Consider adding specific status codes like 500, 502, 503, 504
        )
    ),
    "before_sleep": lambda retry_state: log.warning(
        "Retrying API call",
        attempt=retry_state.attempt_number,
        wait_time=retry_state.next_action.sleep,
        error=retry_state.outcome.exception(),
    ),
    "reraise": True,
}


# --- API Call Function ---
@cached(**cache_config) # Apply caching decorator
@retry(**retry_config) # Apply retry decorator
async def ask_perplexity(
    model: str, prompt: str, system_prompt: str | None = None
) -> dict:
    """
    Asynchronously sends a request to the Perplexity API chat completions endpoint.

    Handles retries, caching, and error logging.

    Args:
        model: The Perplexity model to use (e.g., "sonar-medium-chat").
        prompt: The user's prompt/question.
        system_prompt: An optional system message to guide the model's behavior.

    Returns:
        The JSON response dictionary from the API.

    Raises:
        httpx.HTTPStatusError: If the API returns an error status code after retries.
        httpx.RequestError: If a network or request-related error occurs after retries.
        Exception: For other unexpected errors during the API call.
    """
    request_body = {
        "model": model,
        "messages": [],
    }
    if system_prompt:
        request_body["messages"].append({"role": "system", "content": system_prompt})
    request_body["messages"].append({"role": "user", "content": prompt})

    log.info(
        "Sending request to Perplexity API",
        model=model,
        # Avoid logging full prompt content by default for privacy/size
        prompt_length=len(prompt),
        system_prompt_present=bool(system_prompt),
    )

    try:
        response = await async_client.post("/chat/completions", json=request_body)
        response.raise_for_status() # Raise HTTPStatusError for 4xx/5xx responses
        result = response.json()

        # Log token usage if available in the response
        if "usage" in result:
            log.info(
                "Perplexity API call successful",
                model=model,
                response_id=result.get("id"),
                usage=result["usage"],
            )
        else:
            log.info("Perplexity API call successful", model=model, response_id=result.get("id"))

        return result

    except httpx.HTTPStatusError as e:
        log.error(
            "Perplexity API returned error status",
            status_code=e.response.status_code,
            response_text=e.response.text, # Log error response body
            request_url=str(e.request.url),
            model=model,
            error=e,
        )
        raise # Re-raise after logging
    except httpx.RequestError as e:
        log.error(
            "Error during Perplexity API request",
            request_url=str(e.request.url),
            model=model,
            error=e,
        )
        raise # Re-raise after logging
    except Exception as e:
        log.exception("Unexpected error during Perplexity API call", model=model)
        raise # Re-raise unexpected errors


async def close_client():
    """Closes the shared httpx.AsyncClient."""
    if not async_client.is_closed:
        await async_client.aclose()
        log.info("HTTPX AsyncClient closed.")


# Example usage (consider putting in a main block or separate script)
if __name__ == "__main__":
    import asyncio
    from studyguide.logging_config import configure_logging

    async def main():
        # Ensure logging is configured
        configure_logging(log_level="DEBUG")
        # Ensure PPLX_API_KEY is set in environment or .env file
        if not settings.api.api_key.get_secret_value():
             log.error("PPLX_API_KEY environment variable not set.")
             return

        try:
            response = await ask_perplexity(
                model="sonar-medium-chat",
                prompt="Explain the concept of asynchronous programming in Python.",
                system_prompt="You are a helpful assistant explaining technical concepts clearly.",
            )
            log.info("API Response received", response_id=response.get("id"))
            # print(response) # Avoid printing full response usually

            # Example of cache hit
            log.info("--- Making the same request again (should hit cache) ---")
            response_cached = await ask_perplexity(
                model="sonar-medium-chat",
                prompt="Explain the concept of asynchronous programming in Python.",
                system_prompt="You are a helpful assistant explaining technical concepts clearly.",
            )
            log.info("Cached API Response received", response_id=response_cached.get("id"))
            assert response.get("id") == response_cached.get("id") # IDs should match if cached

        finally:
            await close_client()

    asyncio.run(main())
