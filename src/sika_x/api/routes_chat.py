from collections.abc import Iterator

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from sika_x.core.pipeline import handle_message
from sika_x.models import ChatRequest, ChatResponse, Message

router = APIRouter()


def get_db(request: Request) -> Iterator[Session]:
    session_factory = request.app.state.session_factory
    with session_factory() as db:
        yield db


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ChatResponse:
    msg = Message(
        channel=payload.channel,
        channel_uid=payload.user_id,
        text=payload.text,
    )
    reply = handle_message(msg=msg, db=db, request_id=request.state.request_id)
    return ChatResponse(reply=reply.text, request_id=reply.request_id)
