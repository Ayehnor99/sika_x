from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=4000)
    channel: str = Field(default="api", min_length=1, max_length=32)


class ChatResponse(BaseModel):
    reply: str
    request_id: str


class Message(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    channel: str = Field(min_length=1)
    channel_uid: str = Field(min_length=1)
    text: str = Field(min_length=1, max_length=4000)


class Reply(BaseModel):
    text: str
    request_id: str
