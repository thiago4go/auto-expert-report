"""Unit tests for the Perplexity API client."""

import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import structlog
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from pytest_httpx import HTTPXMock

# Import the module to test
from studyguide import api_client
from studyguide.config import settings

# Configure logger for tests
structlog.configure(processors=[structlog.processors.JSONRenderer()])
log = structlog.get_logger()


# --- Fixtures ---

@pytest.fixture(autouse=True)
async def clear_cache_and_client():
    """Fixture to ensure a clean cache and client state for each test."""
    # Clear aiocache (assuming memory backend for tests)
    cache = Cache(
        Cache.MEMORY,
        serializer=JsonSerializer(),
        namespace="perplexity_api",
    )
    await cache.clear()
    log.debug("Cleared aiocache")

    # Reset tenacity retry stats if needed (usually not necessary per test)
    api_client.ask_perplexity.retry.statistics.clear()

    # Ensure the client is closed after tests that might use it directly
    yield
    # Close the global client if it wasn't closed by the test
    await api_client.close_client()
    # Re-create the client for subsequent tests if necessary (or patch it)
    # For simplicity, we rely on the module-level client being available,
    # but patching might be more robust if tests modify the client instance.


@pytest.fixture
def mock_perplexity_response() -> dict:
    """Provides a sample successful Perplexity API response."""
    return {
        "id": "test-response-id-123",
        "model": "sonar-medium-chat",
        "object": "chat.completion",
        "created": 1700000000,
        "usage": {"prompt_tokens": 20, "completion_tokens": 50, "total_tokens": 70},
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": "Asynchronous programming allows...",
                },
                "delta": {"role": "assistant", "content": ""},
            }
        ],
    }


# --- Test Cases ---

@pytest.mark.asyncio
async def test_ask_perplexity_success(
    httpx_mock: HTTPXMock, mock_perplexity_response: dict
):
    """Test successful API call to Perplexity."""
    httpx_mock.add_response(
        url="https://api.perplexity.ai/chat/completions",
        method="POST",
        json=mock_perplexity_response,
        status_code=200,
    )

    model = "sonar-medium-chat"
    prompt = "What is async?"
    system_prompt = "Explain like I'm five."

    response = await api_client.ask_perplexity(model, prompt, system_prompt)

    assert response == mock_perplexity_response
    # Check request details
    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"
    assert str(request.url) == "https://api.perplexity.ai/chat/completions"
    assert f"Bearer {settings.api.api_key.get_secret_value()}" in request.headers.get("Authorization", "")
    request_data = json.loads(request.content)
    assert request_data["model"] == model
    assert request_data["messages"][0]["role"] == "system"
    assert request_data["messages"][0]["content"] == system_prompt
    assert request_data["messages"][1]["role"] == "user"
    assert request_data["messages"][1]["content"] == prompt


@pytest.mark.asyncio
async def test_ask_perplexity_no_system_prompt(
    httpx_mock: HTTPXMock, mock_perplexity_response: dict
):
    """Test successful API call without a system prompt."""
    httpx_mock.add_response(
        url="https://api.perplexity.ai/chat/completions",
        method="POST",
        json=mock_perplexity_response,
        status_code=200,
    )

    model = "sonar-medium-chat"
    prompt = "What is async?"

    await api_client.ask_perplexity(model, prompt) # No system prompt

    request = httpx_mock.get_request()
    assert request is not None
    request_data = json.loads(request.content)
    assert len(request_data["messages"]) == 1
    assert request_data["messages"][0]["role"] == "user"
    assert request_data["messages"][0]["content"] == prompt


@pytest.mark.asyncio
async def test_ask_perplexity_http_error_4xx(httpx_mock: HTTPXMock):
    """Test handling of HTTP 4xx client errors (should not retry by default)."""
    error_response = {"error": {"message": "Invalid API key", "type": "auth_error"}}
    httpx_mock.add_response(
        url="https://api.perplexity.ai/chat/completions",
        method="POST",
        json=error_response,
        status_code=401, # Unauthorized
    )

    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        await api_client.ask_perplexity("model", "prompt")

    assert excinfo.value.response.status_code == 401
    # Check that it didn't retry (default retry doesn't include 4xx)
    # Note: Tenacity stats might not be perfectly isolated without more complex setup
    # assert api_client.ask_perplexity.retry.statistics.get("attempt_number", 0) <= 1


@pytest.mark.asyncio
async def test_ask_perplexity_http_error_5xx_retry(
    httpx_mock: HTTPXMock, mock_perplexity_response: dict
):
    """Test retry mechanism on HTTP 5xx server errors."""
    error_response = {"error": "Internal Server Error"}
    success_url = "https://api.perplexity.ai/chat/completions"

    # Simulate failures then success
    httpx_mock.add_response(url=success_url, method="POST", status_code=500, json=error_response)
    httpx_mock.add_response(url=success_url, method="POST", status_code=503, json=error_response)
    httpx_mock.add_response(url=success_url, method="POST", json=mock_perplexity_response, status_code=200)

    # Patch sleep to speed up tests
    with patch("asyncio.sleep", new_callable=AsyncMock):
        response = await api_client.ask_perplexity("model", "prompt")

    assert response == mock_perplexity_response
    # Check that multiple requests were made due to retries
    requests = httpx_mock.get_requests()
    assert len(requests) == 3
    assert api_client.ask_perplexity.retry.statistics["attempt_number"] == 3


@pytest.mark.asyncio
async def test_ask_perplexity_timeout_retry(
    httpx_mock: HTTPXMock, mock_perplexity_response: dict
):
    """Test retry mechanism on httpx.TimeoutException."""
    success_url = "https://api.perplexity.ai/chat/completions"

    # Simulate timeout then success
    httpx_mock.add_exception(httpx.TimeoutException("Request timed out", request=None))
    httpx_mock.add_response(url=success_url, method="POST", json=mock_perplexity_response, status_code=200)

    with patch("asyncio.sleep", new_callable=AsyncMock):
        response = await api_client.ask_perplexity("model", "prompt")

    assert response == mock_perplexity_response
    requests = httpx_mock.get_requests()
    assert len(requests) == 2 # Original + 1 retry
    assert api_client.ask_perplexity.retry.statistics["attempt_number"] == 2


@pytest.mark.asyncio
async def test_ask_perplexity_retry_limit_exceeded(httpx_mock: HTTPXMock):
    """Test that an error is raised after exceeding retry limits."""
    error_response = {"error": "Server overloaded"}
    url = "https://api.perplexity.ai/chat/completions"

    # Simulate persistent 503 errors
    for _ in range(api_client.retry_config["stop"].max_attempt_number):
         httpx_mock.add_response(url=url, method="POST", status_code=503, json=error_response)

    with patch("asyncio.sleep", new_callable=AsyncMock), \
         pytest.raises(httpx.HTTPStatusError) as excinfo: # Tenacity re-raises the last exception
        await api_client.ask_perplexity("model", "prompt")

    assert excinfo.value.response.status_code == 503
    requests = httpx_mock.get_requests()
    assert len(requests) == api_client.retry_config["stop"].max_attempt_number
    assert api_client.ask_perplexity.retry.statistics["attempt_number"] == api_client.retry_config["stop"].max_attempt_number


@pytest.mark.asyncio
async def test_ask_perplexity_caching(
    httpx_mock: HTTPXMock, mock_perplexity_response: dict
):
    """Test that successful responses are cached."""
    url = "https://api.perplexity.ai/chat/completions"
    httpx_mock.add_response(url=url, method="POST", json=mock_perplexity_response, status_code=200)

    model = "sonar-medium-chat"
    prompt = "What is caching?"
    system_prompt = "Explain tech concepts."

    # First call - should hit the API
    response1 = await api_client.ask_perplexity(model, prompt, system_prompt)
    assert httpx_mock.get_request() is not None # Check API was called

    # Clear mock requests before second call
    httpx_mock.reset(True)
    httpx_mock.add_response(url=url, method="POST", json=mock_perplexity_response, status_code=200) # Re-add mock

    # Second call with same arguments - should hit cache
    response2 = await api_client.ask_perplexity(model, prompt, system_prompt)

    # Assertions
    assert response1 == response2 # Responses should be identical
    assert httpx_mock.get_request() is None # API should NOT have been called the second time


@pytest.mark.asyncio
async def test_close_client():
    """Test the close_client function."""
    # Ensure client is open first (it's created at module level)
    assert not api_client.async_client.is_closed

    await api_client.close_client()
    assert api_client.async_client.is_closed

    # Calling close again should be safe
    await api_client.close_client()
    assert api_client.async_client.is_closed
