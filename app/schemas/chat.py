from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Source(BaseModel):
    source: Optional[str] = None
    header: Optional[str] = None
    content: Optional[str] = None

class MessageBase(BaseModel):
    role: str
    content: str
    sources: Optional[List[Source]] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None 