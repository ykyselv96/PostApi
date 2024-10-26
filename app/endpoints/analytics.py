from fastapi import APIRouter, Query, status, Depends, BackgroundTasks
from datetime import date
from fastapi_pagination import Page, Params, paginate
from core.get_current_user import get_current_user
from crud.comment_crud import get_comment_crud, CommentCrud
from schemas.post_schema import PostResponse
from schemas.user_schema import User
from schemas.comment_schema import CommentCreationForm, CommentUpdationForm, CommentResponse, CommentStatistic
from sqlalchemy.util import await_only

router = APIRouter(tags=["comment analytics"])


@router.get("/api/comments-daily-breakdown", status_code=status.HTTP_200_OK, response_model=CommentStatistic)
async def get_comments_daily_breakdown(
    date_from: date = Query(..., description="date_from YYYY-MM-DD"),
    date_to: date = Query(..., description="date_to YYYY-MM-DD"),
    comment_crud: CommentCrud = Depends(get_comment_crud)
) -> CommentStatistic:
    res = await comment_crud.get_comments_daily_breakdown(date_from=date_from, date_to=date_to)
    return res
