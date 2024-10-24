from typing import List

from fastapi import APIRouter, status, Depends

from core.connections import async_session
# from core.get_current_user import get_current_user

from core.connections import get_session
from fastapi_pagination import Page, Params, paginate

from crud.post_crud import PostCrud, get_post_crud
from schemas.post_schema import PostCreationForm, PostResponse, PostUpdationForm

from core.get_current_user import get_current_user

from schemas.user_schema import User

from crud.comment_crud import get_comment_crud, CommentCrud
from schemas.comment_schema import CommentResponse, CommentUpdationForm

router = APIRouter(tags=["post management"], prefix="/posts")


@router.post("/", status_code=status.HTTP_200_OK, response_model = PostResponse)
async def add_new_post(payload: PostCreationForm, post_crud: PostCrud = Depends(get_post_crud), curr_user: User = Depends(get_current_user)) -> PostResponse:
    res = await post_crud.create_post(payload=payload, curr_user=curr_user)
    return res



@router.get("/", status_code=status.HTTP_200_OK, response_model = Page[PostResponse])
async def get_all_posts(post_crud: PostCrud = Depends(get_post_crud), params: Params = Depends(),
                        curr_user=Depends(get_current_user)) -> Page[PostResponse]:
    res = await post_crud.get_all_posts()
    return paginate(res, params)


@router.get("/{post_id}", status_code=status.HTTP_200_OK, response_model = PostResponse)
async def get_post_by_id(post_id: int, post_crud: PostCrud = Depends(get_post_crud)) -> PostResponse:
    res = await post_crud.get_post_by_id(post_id=post_id)
    return res



@router.put("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostResponse)
async def update_post(payload: PostUpdationForm, post_id: int, post_crud: PostCrud = Depends(get_post_crud), curr_user=Depends(get_current_user)) -> PostResponse:
    res = await post_crud.update_post(post_id=post_id, payload=payload, curr_user=curr_user)
    return res


@router.delete("/{post_id}",  status_code=status.HTTP_200_OK, response_model=PostResponse)
async def delete_post(post_id: int,  post_crud: PostCrud = Depends(get_post_crud), curr_user=Depends(get_current_user)) -> PostResponse:
    res = await post_crud.delete_post(post_id=post_id, curr_user=curr_user)
    return res


