from sqlalchemy import MetaData, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func


metadata = MetaData()

Base = declarative_base()

class User(Base):
    """Represents a user in the system.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The hashed password of the user.
        comments_reply (Optional[bool]): Indicates if the user can reply to comments, defaults to False.
        auto_reply_delay (Optional[int]): The delay in minutes for automatic replies, defaults to False.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    registred_at = Column(TIMESTAMP, default=func.now())
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="user")
    comments_reply = Column(Boolean, default=False)
    auto_reply_delay = Column(Integer, nullable=True)

class Post(Base):
    """Represents a post created by a user.

    Attributes:
        id (int): The unique identifier of the post.
        title (str): The title of the post (must not be null).
        text (Optional[str]): The content of the post (nullable).
        user_id (int): The identifier of the user who created the post (must not be null).
        author (relationship): The user who authored the post (linked via user_id).
        comments (relationship): The comments associated with the post.
        created_at (TIMESTAMP): The timestamp of when the post was created (defaults to the current time).
        is_blocked (bool): Indicates if the post is blocked, when inappropriate language is present (defaults to False).
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post')
    created_at = Column(TIMESTAMP, default=func.now())
    is_blocked = Column(Boolean, default=False)

class Comment(Base):
    """Represents a comment on a post.

    Attributes:
        id (int): The unique identifier of the comment.
        title (str): The title of the comment (must not be null).
        text (Optional[str]): The content of the comment (nullable).
        post_id (int): The identifier of the post to which the comment belongs (must not be null).
        user_id (int): The identifier of the user who made the comment (must not be null).
        reply_to (Optional[int]): The identifier of the comment when this comment replies to another comment(nullable).


        user (relationship): The user who made the comment (linked via user_id).
        post (relationship): The post to which the comment belongs (linked via post_id).
        parent_comment (relationship): The replies to this comment (if any).
        created_at (TIMESTAMP): The timestamp of when the comment was created (defaults to the current time).
        is_blocked (bool): Indicates if the comment is blocked, when inappropriate language is present  (defaults to False).
    """

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reply_to = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"),nullable=True)
    user = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')
    parent_comment = relationship("Comment", remote_side=[id], backref="replies")
    created_at = Column(TIMESTAMP, default=func.now())
    is_blocked = Column(Boolean, default=False)
