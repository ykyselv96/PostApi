from datetime import datetime
from typing import List
from pydantic import ValidationError
from sqlalchemy import select, update, delete
from fastapi import status, HTTPException, Depends, Request
from core.connections import get_session
from db.models import Post
from fastapi import HTTPException
from schemas.post_schema import PostCreationForm, PostUpdationForm
from schemas.user_schema import User
from schemas.post_schema import PostResponse
from sqlalchemy.orm import selectinload

from schemas.user_schema import UsersResponse

from db.models import Comment


class PostCrud:
    def __init__(self, db):
        self.db = db

    async def if_post_in_db_by_title(self, post_title):
        statement = select(Post).where(Post.title == post_title)
        result = await self.db.execute(statement=statement)
        post_in_db = result.scalars().first()

        if post_in_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='There is already another post with this title',
            )

    async def create_post(self, payload: PostCreationForm, curr_user: User) -> PostResponse:

        await self.if_post_in_db_by_title(post_title=payload.title)

        obj_in = Post(title=payload.title, text=payload.text, user_id=curr_user.id)
        self.db.add(obj_in)

        await self.db.commit()
        return obj_in


    async def get_all_posts(self) -> List[PostResponse]:
        db_result = await self.db.execute(select(Post).options(selectinload(Post.author)))

        posts = db_result.scalars().all()
        response = []
        for post in posts:
            response.append(PostResponse(
            id=post.id,
            title=post.title,
            text=post.text,
            author=UsersResponse(
                id=post.author.id,
                username=post.author.username,
                email=post.author.email,
            )
        ))

        return posts


    async def get_post_by_id(self, post_id: int) -> PostResponse:
        statement = select(Post).options(selectinload(Post.author)).where(Post.id == post_id)

        db_result = await self.db.execute(statement)

        post = db_result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post_not_found")

        return PostResponse(
            id=post.id,
            title=post.title,
            text=post.text,
            author=UsersResponse(
                id=post.author.id,
                username=post.author.username,
                email=post.author.email,
                comments_reply=post.author.comments_reply,
                auto_reply_delay=post.author.auto_reply_delay,
            )
        )


    async def update_post(self, post_id: int, payload: PostUpdationForm, curr_user: User) \
            -> PostResponse:

        post_in_db = await self.get_post_by_id(post_id=post_id)

        if post_in_db and post_in_db.author.id == curr_user.id:

            if payload.title:
                statement = update(Post).where(Post.id == post_id).values(title=payload.title)

            if payload.text:
                statement = statement.values(text=payload.text)

            await self.db.execute(statement)
            await self.db.commit()
            res_in_db = await self.get_post_by_id(post_id=post_id)

            return res_in_db
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can update only your own posts",
            )


    async def delete_post(self, post_id: int, curr_user: User) -> PostResponse:

        post_in_db = await self.get_post_by_id(post_id=post_id)

        if post_in_db and post_in_db.author.id == curr_user.id:

            delete_comments_statement = delete(Comment).where(Comment.post_id == post_id)
            await self.db.execute(delete_comments_statement)

            statement = delete(Post).where(Post.id == post_id)
            await self.db.execute(statement=statement)
            await self.db.commit()
            return post_in_db
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can delete only your own posts",
            )


def get_post_crud(db=Depends(get_session)) -> PostCrud:
    return PostCrud(db=db)
