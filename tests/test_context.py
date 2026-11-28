from sika_x.core.context import build_context, load_persona
from sika_x.models import Message


def test_load_persona_contains_core_rules():
    persona = load_persona()
    assert "sika_x" in persona
    assert "PIN" in persona
    assert "Pidgin" in persona


def test_build_context_wraps_user_message():
    msg = Message(channel="api", channel_uid="ama_01", text="Abeg how far?")
    system_prompt, messages = build_context(msg)

    assert "sika_x" in system_prompt
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert "<user_message>" in messages[0]["content"]
    assert "Abeg how far?" in messages[0]["content"]
