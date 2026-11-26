import pytest
from pydantic import ValidationError

from sika_x.models import ChatRequest


def test_chat_request_valid():
    req = ChatRequest(user_id="kofi_01", text="  Chale how far?  ")
    assert req.user_id == "kofi_01"
    assert req.text == "Chale how far?"
    assert req.channel == "api"


def test_chat_request_rejects_blank_text():
    with pytest.raises(ValidationError):
        ChatRequest(user_id="kofi_01", text="   ")
