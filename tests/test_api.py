import logging

from fastapi.testclient import TestClient
from sqlalchemy import select

from sika_x.api.app import create_app
from sika_x.config import Settings
from sika_x.core.pipeline import FALLBACK_REPLY
from sika_x.db import MessageRow
from sika_x.llm.base import LLMError, LLMResult


def make_test_settings(tmp_path) -> Settings:
    return Settings(
        app_env="test",
        log_level="INFO",
        timezone="Africa/Accra",
        database_url=f"sqlite:///{tmp_path / 'api_test.db'}",
        llm_provider="mock",
        llm_model="none",
    )


class BrokenLLM:
    def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> LLMResult:
        raise LLMError("API down")


def test_health_returns_200(tmp_path):
    app = create_app(make_test_settings(tmp_path))
    client = TestClient(app)

    res = client.get("/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    assert "X-Request-ID" in res.headers


def test_chat_replies_persists_and_logs_request_id(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    app = create_app(make_test_settings(tmp_path))
    client = TestClient(app)

    res = client.post(
        "/v1/chat",
        json={"user_id": "kwame_01", "text": "Chale how far?"},
    )

    assert res.status_code == 200
    body = res.json()
    assert "Chale how far?" in body["reply"]
    request_id = body["request_id"]
    assert res.headers["X-Request-ID"] == request_id
    assert request_id in caplog.text

    with app.state.session_factory() as db:
        rows = db.scalars(
            select(MessageRow).where(MessageRow.request_id == request_id)
        ).all()
        assert len(rows) == 2
        assert rows[1].tokens_in > 0


def test_chat_provider_failure_never_crashes_api(tmp_path):
    app = create_app(make_test_settings(tmp_path), llm_client=BrokenLLM())
    client = TestClient(app)

    res = client.post(
        "/v1/chat",
        json={"user_id": "kwame_01", "text": "Hello"},
    )

    assert res.status_code == 200
    assert res.json()["reply"] == FALLBACK_REPLY


def test_chat_invalid_payload_returns_422(tmp_path):
    app = create_app(make_test_settings(tmp_path))
    client = TestClient(app)

    res = client.post("/v1/chat", json={"user_id": "kwame_01", "text": "   "})

    assert res.status_code == 422
