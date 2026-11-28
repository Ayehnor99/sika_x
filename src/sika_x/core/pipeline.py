import logging

from sqlalchemy.orm import Session

from sika_x.db import MessageRow
from sika_x.models import Message, Reply

logger = logging.getLogger("sika_x.pipeline")


def handle_message(msg: Message, db: Session, request_id: str) -> Reply:
    """M1 walking skeleton pipeline: echo message, persist both turns, return Reply."""
    logger.info(
        "pipeline.receive request_id=%s channel=%s channel_uid=%s",
        request_id,
        msg.channel,
        msg.channel_uid,
    )

    reply_text = f"Echo: {msg.text}"

    user_row = MessageRow(
        request_id=request_id,
        channel=msg.channel,
        channel_uid=msg.channel_uid,
        role="user",
        content=msg.text,
    )
    assistant_row = MessageRow(
        request_id=request_id,
        channel=msg.channel,
        channel_uid=msg.channel_uid,
        role="assistant",
        content=reply_text,
    )
    db.add_all([user_row, assistant_row])
    db.commit()

    logger.info("pipeline.persist request_id=%s saved=2", request_id)
    return Reply(text=reply_text, request_id=request_id)
