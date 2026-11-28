from sqlalchemy import select

from sika_x.core.pipeline import FALLBACK_REPLY, handle_message
from sika_x.db import MessageRow, init_db, make_engine, make_session_factory
from sika_x.llm.base import LLMError, LLMResult
from sika_x.models import Message


class FakeGoodLLM:
    def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> LLMResult:
        return LLMResult(text="Chale I dey!", tokens_in=25, tokens_out=10, cost=0.000112)


class FakeBrokenLLM:
    def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> LLMResult:
        raise LLMError("provider timeout")


def test_handle_message_calls_llm_and_logs_cost(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)
    session_factory = make_session_factory(engine)

    msg = Message(channel="api", channel_uid="ama_01", text="How far?")
    with session_factory() as db:
        reply = handle_message(msg=msg, db=db, request_id="req-llm-1", llm=FakeGoodLLM())

    assert reply.text == "Chale I dey!"
    assert reply.request_id == "req-llm-1"

    with session_factory() as db:
        rows = db.scalars(
            select(MessageRow)
            .where(MessageRow.request_id == "req-llm-1")
            .order_by(MessageRow.id)
        ).all()
        assert len(rows) == 2
        assert [r.role for r in rows] == ["user", "assistant"]
        assert rows[1].tokens_in == 25
        assert rows[1].tokens_out == 10
        assert rows[1].cost == 0.000112


def test_handle_message_uses_fallback_on_llm_error(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)
    session_factory = make_session_factory(engine)

    msg = Message(channel="api", channel_uid="ama_01", text="How far?")
    with session_factory() as db:
        reply = handle_message(msg=msg, db=db, request_id="req-fail-1", llm=FakeBrokenLLM())

    assert reply.text == FALLBACK_REPLY
