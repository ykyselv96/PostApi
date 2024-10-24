from pydantic import BaseModel, Field
from typing import Optional
from schemas.user_schema import UsersResponse
from schemas.post_schema import PostResponse


class CommentCreationForm(BaseModel):
    title: str = Field(..., min_length=1)
    text: str
    # auto_reply_delay: Optional[int] = 0  # Задержка в секундах перед автоматическим ответом
    # reply_to: Optional[int] = None

class CommentUpdationForm(BaseModel):
    title: Optional[str] = Field(..., min_length=1)
    text: Optional[str]

class CommentResponse(BaseModel):
    id: int
    title: str
    text: Optional[str]
    user: UsersResponse

    class Config:
        orm_mode = True
