from pathlib import Path

from sika_x.models import Message

PERSONA_PATH = Path(__file__).with_name("persona.md")


def load_persona(path: Path = PERSONA_PATH) -> str:
    """Load the sika_x system persona prompt from markdown."""
    return path.read_text(encoding="utf-8").strip()


def build_context(msg: Message, persona: str | None = None) -> tuple[str, list[dict[str, str]]]:
    """Build (system_prompt, messages) for the LLM from an incoming Message."""
    system_prompt = persona if persona is not None else load_persona()
    wrapped_text = f"<user_message>\n{msg.text}\n</user_message>"
    messages = [{"role": "user", "content": wrapped_text}]
    return system_prompt, messages
