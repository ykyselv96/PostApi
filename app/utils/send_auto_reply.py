import time
from sqlalchemy.orm import Session
from db.models import Comment
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def send_auto_reply(comment_id: int, delay: int, db: Session):

    delay_in_seconds = delay * 60

    time.sleep(delay_in_seconds)

    statement = (select(Comment).options(selectinload(Comment.post)).options(selectinload(Comment.user))
                 .where(Comment.id == comment_id))

    db_result = await db.execute(statement)
    original_comment = db_result.scalars().first()

    if original_comment:

        auto_reply = Comment(
            title="Auto-reply",
            text="Thank you for your comment. I am currently unavailable to respond promptly, but I will get back to you as soon as possible.",
            post_id=original_comment.post_id,
            user_id=original_comment.user_id,
            reply_to=original_comment.id,
            created_at=datetime.utcnow()
        )

        db.add(auto_reply)
        await db.commit()
