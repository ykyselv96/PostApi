import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from schemas.user_schema import UsersResponse


class CommentCreationForm(BaseModel):
    """Model for creating a comment.

    Attributes:
        title (str): The title of the comment (must be at least 1 character).
        text (str): The content of the comment.
        reply_to (Optional[int]): The ID of the comment being replied to (if it's a comment for another comment).
    """
    title: str = Field(..., min_length=1)
    text: str
    reply_to: Optional[int] = None

class CommentUpdationForm(BaseModel):
    """Model for updating a comment.

     Attributes:
         title (Optional[str]): The new title of the comment (must be at least 1 character if provided).
         text (Optional[str]): The new content of the comment (if provided).
     """
    title: Optional[str] = Field(..., min_length=1)
    text: Optional[str]

class CommentResponse(BaseModel):
    """Model for representing a comment.

    Attributes:
        id (int): The unique identifier of the comment.
        title (str): The title of the comment.
        text (Optional[str]): The content of the comment (if provided).
        is_blocked (bool): Whether the comment is blocked when inappropriate language is present
        created_at (datetime.datetime): The date and time the comment was created.
        user (UsersResponse): The user who created the comment.
    """
    id: int
    title: str
    text: Optional[str]
    is_blocked: bool
    created_at: datetime.datetime
    user: UsersResponse

    class Config:
        orm_mode = True


class CommentStatisticOneDay(BaseModel):
    """Model for representing a comment.

    Attributes:
        id (int): The unique identifier of the comment.
        title (str): The title of the comment.
        text (Optional[str]): The content of the comment (if provided).
        user (UsersResponse): The user who created the comment.
    """
    date: datetime.date
    created_comments_amount: int
    blocked_comments_amount: int
    total_comments_amount: int


class CommentStatistic(BaseModel):
    comments_statistic_per_day: List[CommentStatisticOneDay]
    comments_total_amount: int
