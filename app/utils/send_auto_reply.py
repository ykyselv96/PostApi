import time
from sqlalchemy.orm import Session
import vertexai
from vertexai.generative_models import GenerativeModel
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.models import Comment
from core.config.system_config import settings


async def send_auto_reply(comment_id: int, delay: int, db: Session):
    """
    Sends an automatic reply to a comment after a specified delay.

    Args:
        comment_id (int): The ID of the comment to reply to.
        delay (int): The delay in minutes before sending the reply.
        db (Session): Database session for executing operations.

    Returns:
        None: The function does not return a value; it commits the reply to the database.
    """

    delay_in_seconds = delay * 60

    time.sleep(delay_in_seconds)

    statement = (select(Comment).options(selectinload(Comment.post)).options(selectinload(Comment.user))
                 .where(Comment.id == comment_id))

    db_result = await db.execute(statement)
    original_comment = db_result.scalars().first()


    if original_comment:
        vertexai.init(project=settings.google_cloud_project_id, location="us-central1")

        model = GenerativeModel("gemini-1.5-flash-002")

        response = model.generate_content(
            f"Please, make autoreply for this comment: {original_comment.text}. It should be simple(as autoreply) and don't have options"
        )
        print("DDDD",response.text)
        auto_reply = Comment(
            title="Auto-reply",
            text=response.text,
            post_id=original_comment.post_id,
            user_id=original_comment.user_id,
            reply_to=original_comment.id,
            created_at=datetime.utcnow()
        )

        db.add(auto_reply)
        await db.commit()
