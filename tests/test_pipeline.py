from sqlalchemy import select

from sika_x.core.pipeline import handle_message
from sika_x.db import MessageRow, init_db, make_engine, make_session_factory
from sika_x.models import Message


def test_handle_message_echoes_and_persists(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)
    session_factory = make_session_factory(engine)

    msg = Message(channel="api", channel_uid="ama_01", text="Chale test")
    with session_factory() as db:
        reply = handle_message(msg=msg, db=db, request_id="req-test-1")

    assert reply.text == "Echo: Chale test"
    assert reply.request_id == "req-test-1"

    with session_factory() as db:
        rows = db.scalars(
            select(MessageRow)
            .where(MessageRow.request_id == "req-test-1")
            .order_by(MessageRow.id)
        ).all()
        assert len(rows) == 2
        assert [r.role for r in rows] == ["user", "assistant"]
        assert rows[0].content == "Chale test"
        assert rows[1].content == "Echo: Chale test"
