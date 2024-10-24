import uuid

from sqlalchemy import MetaData, Column, Integer, String, TIMESTAMP, ForeignKey, Table, Text, Boolean
from sqlmodel import Field, SQLModel

from sqlalchemy.orm import declarative_base, relationship, CascadeOptions
from sqlalchemy.sql import func


metadata = MetaData()

Base = declarative_base()

class User(Base):
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
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post')
    created_at = Column(TIMESTAMP, default=func.now())

class Comment(Base):
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

