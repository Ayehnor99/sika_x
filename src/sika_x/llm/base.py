from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMResult:
    text: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost: float = 0.0


class LLMError(Exception):
    """Raised when an LLM provider fails to return a valid reply."""


class LLMClient(Protocol):
    def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> LLMResult:
        """Generate a reply given a system prompt and chat turns."""
        ...
