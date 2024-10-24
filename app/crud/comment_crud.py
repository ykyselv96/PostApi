from datetime import datetime
from typing import List

import asyncpg
from pydantic import ValidationError
from sqlalchemy import select, update, delete
from fastapi import status, HTTPException, Depends, Request, BackgroundTasks
from core.connections import get_session
from db.models import Post, Comment
from fastapi import HTTPException
from schemas.user_schema import User
from schemas.post_schema import PostResponse

from sqlalchemy.orm import selectinload

from schemas.comment_schema import CommentResponse

from sqlalchemy.exc import IntegrityError

from crud.post_crud import get_post_crud

from schemas.user_schema import UsersResponse
from schemas.post_schema import PostResponse

from schemas.comment_schema import CommentUpdationForm, CommentCreationForm

from utils.send_auto_reply import send_auto_reply


class CommentCrud:
    def __init__(self, db):
        self.db = db


    async def add_new_comment_to_post(self, post_id: int, background_tasks: BackgroundTasks, payload: CommentCreationForm, curr_user: User) -> CommentResponse:

        post_crud = get_post_crud(self.db)

        post = await post_crud.get_post_by_id(post_id=post_id)

        obj_in = Comment(title=payload.title, text=payload.text, user_id=curr_user.id, post_id=post_id)

        self.db.add(obj_in)
        await self.db.commit()

        if post.author.comments_reply:
            background_tasks.add_task(
                send_auto_reply,
                comment_id=obj_in.id,
                delay=post.author.auto_reply_delay,
                db=self.db
            )
        return obj_in


    async def get_all_comments_to_post(self, post_id: int) -> List[CommentResponse]:

        post_crud = get_post_crud(self.db)

        await post_crud.get_post_by_id(post_id=post_id)

        db_result = await self.db.execute(select(Comment).options(selectinload(Comment.post)).options(selectinload(Comment.user)).where(Comment.post_id == post_id))

        comments = db_result.scalars().all()

        response = []
        for comment in comments:
            response.append(CommentResponse(
                id=comment.id,
                title=comment.title,
                text=comment.text,
                user=UsersResponse(
                    id=comment.user.id,
                    username=comment.user.username,
                    email=comment.user.email
                ))
            )

        return response


    async def get_comment_to_post_by_comment_id(self, post_id: int, comment_id: int) -> CommentResponse:

        statement = (select(Comment).options(selectinload(Comment.post)).options(selectinload(Comment.user))
                     .where(Comment.post_id==post_id, Comment.id == comment_id))

        db_result = await self.db.execute(statement)

        comment = db_result.scalars().first()

        if not comment:
            raise HTTPException(status_code=404, detail="Comment_not_found")

        return CommentResponse(
                id=comment.id,
                title=comment.title,
                text=comment.text,
                user=UsersResponse(
                    id=comment.user.id,
                    username=comment.user.username,
                    email=comment.user.email,
                ),
            )


    async def update_comment_to_post(self, post_id: int, comment_id: int, payload: CommentUpdationForm, curr_user: User) \
            -> CommentResponse:

        comment_in_db = await self.get_comment_to_post_by_comment_id(post_id=post_id, comment_id=comment_id)

        if comment_in_db and comment_in_db.user.id == curr_user.id:

            if payload.title:
                statement = update(Comment).where(Comment.id == comment_id).values(title=payload.title)

            if payload.text:
                statement = statement.values(text=payload.text)

            await self.db.execute(statement)
            await self.db.commit()
            comment_in_db = await self.get_comment_to_post_by_comment_id(post_id=post_id, comment_id=comment_id)

            return comment_in_db

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can update only your own comments",
            )


    async def delete_comment(self, post_id: int, comment_id: int, curr_user: User) -> CommentResponse:

        comment_in_db = await self.get_comment_to_post_by_comment_id(post_id=post_id, comment_id=comment_id)

        if comment_in_db and comment_in_db.user.id == curr_user.id:
            statement = delete(Comment).where(Comment.id == comment_id)
            await self.db.execute(statement=statement)
            await self.db.commit()
            return comment_in_db
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can delete only your own comments",
            )


def get_comment_crud(db=Depends(get_session)) -> CommentCrud:
    return CommentCrud(db=db)