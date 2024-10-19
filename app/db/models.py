import uuid

from sqlalchemy import MetaData, Column, Integer, String, TIMESTAMP, ForeignKey, Table, Text
from sqlmodel import Field, SQLModel

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func


metadata = MetaData()

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    description = Column(String, nullable=True)
    registred_at = Column(TIMESTAMP, default=func.now())


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='posts')

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')
