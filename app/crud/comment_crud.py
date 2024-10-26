from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy import select, update, delete, func, and_
from fastapi import status, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import selectinload
from core.connections import get_session
from db.models import Post, Comment
from schemas.user_schema import User, UsersResponse
from schemas.comment_schema import CommentResponse, CommentUpdationForm, CommentCreationForm, CommentStatistic, CommentStatisticOneDay
from crud.post_crud import get_post_crud
from utils.send_auto_reply import send_auto_reply
from utils.policy_check import policy_check


class CommentCrud:
    def __init__(self, db):
        self.db = db

    async def add_new_comment_to_post(self, post_id: int, background_tasks: BackgroundTasks, payload: CommentCreationForm, curr_user: User) -> CommentResponse:

        post_crud = get_post_crud(self.db)

        post = await post_crud.get_post_by_id(post_id=post_id)

        if payload.reply_to > 0:
            await self.get_comment_to_post_by_comment_id(post_id=post_id, comment_id=payload.reply_to)
        else:
            payload.reply_to = None

        if post.is_blocked:
            is_blocked = post.is_blocked
        else:
            is_blocked = policy_check(title=payload.title, text=payload.text)

        obj_in = Comment(title=payload.title, text=payload.text, user_id=curr_user.id, post_id=post_id, reply_to=payload.reply_to, is_blocked=is_blocked)

        self.db.add(obj_in)
        await self.db.commit()

        if is_blocked:
            raise HTTPException(status_code=403, detail="Your comment contains prohibited content and has been blocked.")

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


    async def get_comments_daily_breakdown(self, date_from, date_to) -> CommentStatistic:
        if date_from > date_to:
            raise HTTPException(status_code=400, detail="The start date must be less than or equal to the end date.")

        statement = select(
            func.date(Comment.created_at).label('date'),
            func.count().filter(Comment.is_blocked == False).label('created_comments'),
            func.count().filter(Comment.is_blocked == True).label('blocked_comments'),
            func.count("*").label('total'),
        ).where(
            and_(Comment.created_at>=date_from, Comment.created_at < (date_to + timedelta(days=1)))
        ).group_by(
            func.date(Comment.created_at)
        ).order_by(
            'date'
        )

        result = await self.db.execute(statement)

        response = result.mappings().all()

        statement_for_total = select(
            func.count("*").label('total')
                ).where(
                and_(
                Comment.created_at >= date_from,
                Comment.created_at < (date_to + timedelta(days=1))
                )
            )
        total = (await self.db.execute(statement_for_total)).scalar()

        return CommentStatistic(comments_statistic_per_day=[CommentStatisticOneDay
                            (date=el.get('date'), created_comments_amount=el.get('created_comments'),
                            blocked_comments_amount=el.get('blocked_comments'), total_comments_amount=el.get('total'))
                            for el in response], comments_total_amount=total)


def get_comment_crud(db=Depends(get_session)) -> CommentCrud:
    return CommentCrud(db=db)
