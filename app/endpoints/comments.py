from fastapi import APIRouter, status, Depends, BackgroundTasks
from fastapi_pagination import Page, Params, paginate
from core.get_current_user import get_current_user
from crud.comment_crud import get_comment_crud, CommentCrud
from schemas.post_schema import PostResponse
from schemas.user_schema import User
from schemas.comment_schema import CommentCreationForm, CommentUpdationForm, CommentResponse


router = APIRouter(tags=["comments management"], prefix="/posts")


@router.post("/{post_id}/comments", status_code=status.HTTP_200_OK, response_model=CommentResponse)
async def add_new_comment_to_post(payload: CommentCreationForm, post_id: int, background_tasks: BackgroundTasks,
                                  comment_crud: CommentCrud = Depends(get_comment_crud),
                                  curr_user: User = Depends(get_current_user)) -> CommentResponse:
    res = await comment_crud.add_new_comment_to_post(post_id=post_id, payload=payload,
                                                     background_tasks=background_tasks, curr_user=curr_user)
    return res


@router.get("/{post_id}/comments", status_code=status.HTTP_200_OK, response_model=Page[CommentResponse])
async def get_all_comments_to_post(post_id: int, comment_crud: CommentCrud = Depends(get_comment_crud),
                                   params: Params = Depends(),
                                   curr_user=Depends(get_current_user)) -> Page[PostResponse]:
    res = await comment_crud.get_all_comments_to_post(post_id=post_id)
    return paginate(res, params)


@router.get("/{post_id}/comments/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentResponse)
async def get_comment_to_post_by_comment_id(post_id: int, comment_id: int,
                                            comment_crud: CommentCrud = Depends(get_comment_crud),
                                            curr_user=Depends(get_current_user)) -> Page[PostResponse]:
    res = await comment_crud.get_comment_to_post_by_comment_id(post_id=post_id, comment_id=comment_id)
    return res


@router.put("{post_id}/comments/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentResponse)
async def update_comment_to_post(payload: CommentUpdationForm, post_id: int, comment_id: int,
                                 comment_crud: CommentCrud = Depends(get_comment_crud),
                                 curr_user=Depends(get_current_user)) -> CommentResponse:
    res = await comment_crud.update_comment_to_post(post_id=post_id, comment_id=comment_id, payload=payload,
                                                    curr_user=curr_user)
    return res


@router.delete("{post_id}/comments/{comment_id}",  status_code=status.HTTP_200_OK, response_model=CommentResponse)
async def delete_comment(post_id: int, comment_id: int,  comment_crud: CommentCrud = Depends(get_comment_crud),
                         curr_user=Depends(get_current_user)) -> PostResponse:
    res = await comment_crud.delete_comment(post_id=post_id, comment_id=comment_id, curr_user=curr_user)
    return res
