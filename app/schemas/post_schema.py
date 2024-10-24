from pydantic import BaseModel, Field
from typing import Optional

from schemas.user_schema import UsersResponse


class PostCreationForm(BaseModel):
    title: str = Field(..., min_length=1)
    text: str

class PostUpdationForm(BaseModel):
    title: Optional[str] = Field(..., min_length=1)
    text: Optional[str]

class PostResponse(BaseModel):
    id: int
    title: str
    text: Optional[str]
    author: UsersResponse

    class Config:
        orm_mode = True
