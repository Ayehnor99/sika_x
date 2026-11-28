import logging

from sqlalchemy.orm import Session

from sika_x.core.context import build_context
from sika_x.db import MessageRow
from sika_x.llm.base import LLMClient, LLMError
from sika_x.llm.provider import MockLLMClient
from sika_x.models import Message, Reply

logger = logging.getLogger("sika_x.pipeline")

FALLBACK_REPLY = (
    "Chale, my brain dey slow small right now. Abeg try again in a few seconds!"
)


def handle_message(
    msg: Message,
    db: Session,
    request_id: str,
    llm: LLMClient | None = None,
) -> Reply:
    """Run message through context builder, LLM call (with fallback), and DB persistence."""
    logger.info(
        "pipeline.receive request_id=%s channel=%s channel_uid=%s",
        request_id,
        msg.channel,
        msg.channel_uid,
    )

    client = llm if llm is not None else MockLLMClient()
    system_prompt, prompt_messages = build_context(msg)

    tokens_in = 0
    tokens_out = 0
    cost = 0.0
    try:
        result = client.generate(system_prompt=system_prompt, messages=prompt_messages)
        reply_text = result.text
        tokens_in = result.tokens_in
        tokens_out = result.tokens_out
        cost = result.cost
        logger.info(
            "pipeline.llm request_id=%s tokens_in=%d tokens_out=%d cost=%.6f",
            request_id,
            tokens_in,
            tokens_out,
            cost,
        )
    except (LLMError, Exception) as exc:
        logger.warning("pipeline.llm_fallback request_id=%s error=%s", request_id, exc)
        reply_text = FALLBACK_REPLY

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
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost=cost,
    )
    db.add_all([user_row, assistant_row])
    db.commit()

    logger.info("pipeline.persist request_id=%s saved=2", request_id)
    return Reply(text=reply_text, request_id=request_id)
