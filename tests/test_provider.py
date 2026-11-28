import httpx
import pytest

from sika_x.llm.base import LLMError
from sika_x.llm.provider import GeminiClient, MockLLMClient


def test_mock_llm_client_returns_result():
    client = MockLLMClient()
    res = client.generate("system", [{"role": "user", "content": "Yo"}])
    assert "Yo" in res.text
    assert res.tokens_in > 0


def test_gemini_client_parses_reply_skips_thoughts_and_costs():
    captured_headers = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(dict(request.headers))
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"thought": True, "text": "secret internal reasoning"},
                                {"text": "Chale, I dey! How I fit help you?"},
                            ]
                        }
                    }
                ],
                "usageMetadata": {
                    "promptTokenCount": 100,
                    "candidatesTokenCount": 20,
                    "totalTokenCount": 150,
                },
            },
        )

    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = GeminiClient(api_key="test-key-123", model="gemini-4-hydrogen", http_client=http)

    res = client.generate("Be brief.", [{"role": "user", "content": "How far?"}])

    assert captured_headers["x-goog-api-key"] == "test-key-123"
    assert res.text == "Chale, I dey! How I fit help you?"
    assert "secret internal reasoning" not in res.text
    assert res.tokens_in == 100
    assert res.tokens_out == 50
    assert res.cost == round((100 / 1_000_000) * 1.50 + (50 / 1_000_000) * 7.50, 6)


def test_gemini_client_retries_once_on_503():
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] == 1:
            return httpx.Response(503, json={"error": "overloaded"})
        return httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": "Back online!"}]}}]},
        )

    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = GeminiClient(api_key="test-key-123", http_client=http)

    res = client.generate("sys", [{"role": "user", "content": "Hi"}])

    assert attempts["count"] == 2
    assert res.text == "Back online!"


def test_gemini_client_raises_llm_error_when_retry_exhausted():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "server down"})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = GeminiClient(api_key="test-key-123", http_client=http)

    with pytest.raises(LLMError):
        client.generate("sys", [{"role": "user", "content": "Hi"}])
