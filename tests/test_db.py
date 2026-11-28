from sqlalchemy import select

from sika_x.db import MessageRow, init_db, make_engine, make_session_factory


def test_save_and_read_message(tmp_path):
    db_file = tmp_path / "test.db"
    engine = make_engine(f"sqlite:///{db_file}")
    init_db(engine)
    session_factory = make_session_factory(engine)

    with session_factory() as db:
        row = MessageRow(
            request_id="req-123",
            channel="api",
            channel_uid="kofi_01",
            role="user",
            content="Chale how far?",
        )
        db.add(row)
        db.commit()

    with session_factory() as db:
        saved = db.scalar(select(MessageRow).where(MessageRow.request_id == "req-123"))
        assert saved is not None
        assert saved.content == "Chale how far?"
        assert saved.role == "user"
        assert saved.cost == 0.0
