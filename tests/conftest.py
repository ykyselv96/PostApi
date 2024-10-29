import asyncio
from typing import AsyncGenerator

import pytest
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from sqlalchemy.pool import NullPool
from faker import Faker
from datetime import datetime
from sqlalchemy import text

from core.connections import get_session
from core.config.system_config import settings
from db.models import metadata, Base


async def override_get_session():
    async with async_session() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session

engine_test = create_async_engine(settings.TEST_DATABASE_URI, poolclass=NullPool, echo=True)
async_session = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
metadata.bind = engine_test


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():

    async with engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with async_session() as session:
        yield session  # Возвращает сессию для использования в тестах
        await session.rollback()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_app():
    client = httpx.Client(transport=httpx.WSGITransport(app=app))
    yield client


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope='session')
def users_tokens():
    tokens_store = dict()
    return tokens_store


@pytest.fixture(scope='session')
async def login_user(ac: AsyncClient, users_tokens):
    async def __send_request(user_email: str, user_password: str):
        payload = {
            "email": user_email,
            "password": user_password,
        }
        response = await ac.post("/users/login", json=payload)
        if response.status_code != 200:
            return response
        user_token = response.json().get('access_token')
        users_tokens[user_email] = user_token
        return response

    return __send_request

fake = Faker()

mock_comments = [{'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 23, 14, 30, 45),
                  'user_id': 6, 'post_id': 6, 'is_blocked': False},

                 {'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 28, 11, 10, 49),
                  'user_id': 6, 'post_id': 6, 'is_blocked': True},

                 {'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 28, 17, 9, 45),
                  'user_id': 6, 'post_id': 6, 'is_blocked': False},

                 {'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 29, 11, 30, 0), 'user_id': 6,
                  'post_id': 6, 'is_blocked': True},

                 {'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 30, 21, 35, 5),
                  'user_id': 6, 'post_id': 6, 'is_blocked': False},

                 {'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 28, 10, 28, 12),
                  'user_id': 6, 'post_id': 6, 'is_blocked': False},

                 {'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 28, 11, 10, 49),
                  'user_id': 6, 'post_id': 6, 'is_blocked': True},

                 {'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 22, 17, 9, 45),
                  'user_id': 6, 'post_id': 6, 'is_blocked': False},

                 {'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 29, 18, 3, 0), 'user_id': 6,
                  'post_id': 6, 'is_blocked': True},

                 {'title': fake.text(), 'text': fake.text(),
                  'created_at': datetime(2024, 10, 30, 22, 35, 9),
                  'user_id': 6, 'post_id': 6, 'is_blocked': False},
                 ]


@pytest.fixture
async def setup_fake_data(db_session):

    await db_session.execute(
        text("""
                INSERT INTO users (id,email,username,password,registred_at)
                VALUES (:id, :email, :username, :password, :registred_at)
                """),
        {"id": 6, "email": "user6@gmail.com", "username": "username", "password": "password*6666",
         "registred_at": datetime.utcnow()}
    )

    await db_session.execute(
        text("""
                 INSERT INTO posts (id, title, text, user_id, created_at, is_blocked)
                 VALUES (:id, :title, :text, :user_id, :created_at, :is_blocked)
                 """),
        {"id": 6, "title": "post 6", "text": "test_post_6", "user_id": 6, "created_at": datetime.utcnow(),
         "is_blocked": False}
    )
    await db_session.commit()

    await db_session.execute(
        text("""
               INSERT INTO comments (title, text, created_at, user_id, post_id, is_blocked)
               VALUES (:title, :text, :created_at, :user_id, :post_id, :is_blocked)
           """),
        mock_comments

    )

    await db_session.commit()

    yield

    await db_session.execute(text("DELETE FROM comments WHERE post_id=6"))
    await db_session.execute(text("DELETE FROM posts WHERE id = 6"))
    await db_session.execute(text("DELETE FROM users WHERE id = 6"))
    await db_session.commit()
