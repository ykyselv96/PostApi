from typing import List
from sqlalchemy import select, update, delete
from fastapi import status, Depends, HTTPException
from sqlalchemy.orm import selectinload
import vertexai
from vertexai.generative_models import GenerativeModel
from core.config.system_config import settings
from core.connections import get_session
from db.models import Post,  Comment
from schemas.post_schema import PostCreationForm, PostUpdationForm, PostResponse
from schemas.user_schema import User, UsersResponse


class PostCrud:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def policy_check(title: str, text: str) -> bool:
        """
        Checks the provided title and text for inappropriate language or offensive expressions.

        Args:
            title (str): The title to analyze.
            text (str): The text to analyze.

        Returns:
            bool: A response indicating whether inappropriate language is present (True or False).
        """
        vertexai.init(project=settings.google_cloud_project_id, location="us-central1")

        model = GenerativeModel("gemini-1.5-flash-002")

        response = model.generate_content(
            f"Are there any vulgar, inappropriate language, racism, or offensive expressions (all languages) "
            f"in the '{title}' or in the '{text}'? Answer: 'yes/no'"
        )

        if response.text == 'yes\n' or response.text == 'Yes\n':
            return True

        return False

    async def if_post_in_db_by_title(self, post_title) -> bool:
        statement = select(Post).where(Post.title == post_title)
        result = await self.db.execute(statement=statement)
        post_in_db = result.mappings().first()

        if post_in_db:
            return True
        return False

    async def create_post(self, payload: PostCreationForm, curr_user: User) -> PostResponse:

        post_in_db = await self.if_post_in_db_by_title(post_title=payload.title)

        if post_in_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='There is already another post with this title',
            )

        is_blocked = self.policy_check(title=payload.title, text=payload.text)

        obj_in = Post(title=payload.title, text=payload.text, user_id=curr_user.id, is_blocked=is_blocked)
        self.db.add(obj_in)
        await self.db.commit()

        if is_blocked:
            raise HTTPException(status_code=403, detail="Your post contains prohibited content and has been blocked.")

        return obj_in

    async def get_all_posts(self) -> List[PostResponse]:
        db_result = await self.db.execute(select(Post).options(selectinload(Post.author)))

        posts = db_result.scalars().all()
        response = []
        for post in posts:
            response.append(
                PostResponse(
                    id=post.id,
                    title=post.title,
                    text=post.text,
                    created_at=post.created_at,
                    is_blocked=post.is_blocked,
                    author=UsersResponse(
                        id=post.author.id,
                        username=post.author.username,
                        email=post.author.email,
                    )
                )
            )

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
            created_at=post.created_at,
            is_blocked=post.is_blocked,
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
        is_blocked = self.policy_check(title=payload.title, text=payload.text)

        if post_in_db and post_in_db.author.id == curr_user.id:

            if payload.title:
                statement = update(Post).where(Post.id == post_id).values(title=payload.title, is_blocked=is_blocked)

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
