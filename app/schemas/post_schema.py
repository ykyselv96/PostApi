import datetime
from pydantic import BaseModel, Field
from typing import Optional
from schemas.user_schema import UsersResponse


class PostCreationForm(BaseModel):
    """Model for creating a post.

    Attributes:
        title (str): The title of the post (must be at least 1 character).
        text (str): The content of the post.
    """
    title: str = Field(..., min_length=1)
    text: str


class PostUpdationForm(BaseModel):
    """Model for updating a post.

    Attributes:
        title (Optional[str]): The new title of the post (must be at least 1 character if provided).
        text (Optional[str]): The new content of the post (if provided).
    """
    title: Optional[str] = Field(..., min_length=1)
    text: Optional[str]


class PostResponse(BaseModel):
    """Model for representing a post response.

    Attributes:
        id (int): The unique identifier of the post.
        title (str): The title of the post.
        text (Optional[str]): The content of the post (if provided).
        is_blocked (bool): Whether the post is blocked when inappropriate language is present
        created_at (datetime.datetime): The date and time the post was created.
        author (UsersResponse): The author of the post.
    """
    id: int
    title: str
    text: Optional[str]
    is_blocked: bool
    created_at: datetime.datetime
    author: UsersResponse

    class Config:
        orm_mode = True
