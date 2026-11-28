import httpx

from sika_x.config import Settings
from sika_x.llm.base import LLMClient, LLMError, LLMResult

# (input_usd_per_1m, output_usd_per_1m)
MODEL_PRICING_PER_1M: dict[str, tuple[float, float]] = {
    "gemini-3.5-flash-lite": (0.30, 2.50),
}


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    in_rate, out_rate = MODEL_PRICING_PER_1M.get(model, (1.50, 7.50))
    cost = (tokens_in / 1_000_000) * in_rate + (tokens_out / 1_000_000) * out_rate
    return round(cost, 6)


class MockLLMClient:
    """Deterministic local LLM client for offline development and tests."""

    def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> LLMResult:
        last_text = messages[-1]["content"] if messages else ""
        return LLMResult(
            text=f"Mock reply: {last_text}",
            tokens_in=10,
            tokens_out=12,
            cost=0.000105,
        )


class GeminiClient:
    """HTTP client for Google Gemini generateContent API."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-4-hydrogen",
        timeout: float = 30.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("LLM_API_KEY is required for Gemini provider")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._http_client = http_client

    def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> LLMResult:
        url = f"{self.BASE_URL}/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        contents = [
            {
                "role": "model" if m["role"] == "assistant" else "user",
                "parts": [{"text": m["content"]}],
            }
            for m in messages
        ]
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": {"maxOutputTokens": 2048},
        }

        last_err: Exception | None = None
        for attempt in range(2):
            try:
                data = self._post(url, headers, payload)
                return self._parse_response(data)
            except LLMError as exc:
                last_err = exc
                if attempt == 0:
                    continue
            except httpx.HTTPError as exc:
                last_err = LLMError(f"Gemini request error: {type(exc).__name__}")
                if attempt == 0:
                    continue

        raise LLMError(str(last_err) if last_err else "Gemini request failed")

    def _post(self, url: str, headers: dict[str, str], payload: dict) -> dict:
        if self._http_client is not None:
            res = self._http_client.post(url, headers=headers, json=payload, timeout=self.timeout)
        else:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, headers=headers, json=payload)

        if res.status_code >= 500 or res.status_code == 429:
            raise LLMError(f"Gemini transient error HTTP {res.status_code}")
        if res.status_code >= 400:
            raise LLMError(f"Gemini rejected request HTTP {res.status_code}")
        return res.json()

    def _parse_response(self, data: dict) -> LLMResult:
        candidates = data.get("candidates") or []
        if not candidates:
            raise LLMError("Gemini returned no candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        visible_chunks = [p["text"] for p in parts if "text" in p and not p.get("thought")]
        text = "".join(visible_chunks).strip()
        if not text:
            raise LLMError("Gemini returned empty text")

        usage = data.get("usageMetadata", {})
        tokens_in = int(usage.get("promptTokenCount", 0))
        total_tokens = int(usage.get("totalTokenCount", 0))
        if total_tokens > 0:
            tokens_out = max(0, total_tokens - tokens_in)
        else:
            tokens_out = int(usage.get("candidatesTokenCount", 0)) + int(
                usage.get("thoughtsTokenCount", 0)
            )

        return LLMResult(
            text=text,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=estimate_cost(self.model, tokens_in, tokens_out),
        )


def build_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider == "mock":
        return MockLLMClient()
    if settings.llm_provider == "gemini":
        return GeminiClient(api_key=settings.llm_api_key, model=settings.llm_model)
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
