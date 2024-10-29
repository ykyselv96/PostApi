from typing import List
from jose import jwt
from datetime import datetime, timedelta
import math
from sqlalchemy import select, delete, update
from fastapi import status, HTTPException, Depends
from schemas.user_schema import UsersResponse, SignupForm, UserUpdateForm
from core.connections import get_session
from core.config import system_config
from db.models import User
from utils.hash_password import check_password


class UserCrud:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def create_access_token(user_email) -> str:

        expires_delta = datetime.utcnow() + timedelta(minutes=int(system_config.settings.access_token_expire_minutes))

        to_encode = {"exp": expires_delta, "sub": str(user_email)}
        encoded_jwt = jwt.encode(to_encode, system_config.settings.jwt_access_secret_key,
                                 system_config.settings.algorithm)

        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_email) -> str:

        refresh_token_expire_minutes = math.prod(
            [int(el) for el in system_config.settings.refresh_token_expire_minutes.split('*')])

        expires_delta = datetime.utcnow() + timedelta(minutes=int(refresh_token_expire_minutes))

        to_encode = {"exp": expires_delta, "sub": str(user_email)}
        encoded_jwt = jwt.encode(to_encode, system_config.settings.jwt_refresh_secret_key,
                                 system_config.settings.algorithm)
        return encoded_jwt

    async def if_user_in_db_by_username(self, username) -> UsersResponse:
        statement = select(User).where(User.username == username)
        result = await self.db.execute(statement=statement)
        user_in_db = result.scalars().first()

        if user_in_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='There is already another user with this username',
            )

    async def if_user_in_db(self, payload: SignupForm) -> UsersResponse:
        await self.if_user_in_db_by_username(username=payload.username)

        statement = select(User).where(User.email == payload.email)
        result = await self.db.execute(statement=statement)
        user_in_db = result.scalars().first()

        if user_in_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='There is already another user with this email',
            )

    async def create_user(self, payload: SignupForm) -> UsersResponse:

        await self.if_user_in_db(payload=payload)
        obj_in = User(**payload.dict(exclude={'password_repeat'}))
        self.db.add(obj_in)
        await self.db.commit()
        return obj_in

    async def get_user_by_email(self, email: str) -> UsersResponse:
        statement = select(User).where(User.email == email)
        user_in_db = (await self.db.execute(statement)).scalars().first()

        if not user_in_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_in_db

    async def get_user_by_email_and_password(self, email: str, password: str) -> UsersResponse:

        user_in_db = await self.get_user_by_email(email=email)
        password_check = check_password(password=password, hashed_password=user_in_db.password)

        if not password_check:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_in_db

    async def get_all_users(self) -> List[UsersResponse]:
        db_result = await self.db.execute(select(User))
        return db_result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> UsersResponse:
        statement = select(User).where(User.id == user_id)
        db_result = await self.db.execute(statement)
        user = db_result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User_not_found")

        return user

    async def update_user(self, payload: UserUpdateForm, user_id: int) -> UsersResponse:

        await self.get_user_by_id(user_id=user_id)

        statement = update(User).where(User.id == user_id)

        if payload.password:
            statement = statement.values(password=payload.password)

        if payload.username:
            await self.if_user_in_db_by_username(username=payload.username)
            statement = statement.values(username=payload.username)

        if payload.email:
            statement = statement.values(email=payload.email)

        if payload.comments_reply:
            statement = statement.values(comments_reply=payload.comments_reply)

        if payload.auto_reply_delay:
            statement = statement.values(auto_reply_delay=payload.auto_reply_delay)

        await self.db.execute(statement=statement)
        await self.db.commit()

        res_in_db = await self.get_user_by_id(user_id)

        return res_in_db

    async def delete_user(self, user_id: int) -> UsersResponse:

        user_in_db = await self.get_user_by_id(user_id=user_id)
        statement = delete(User).where(User.id == user_id)
        await self.db.execute(statement=statement)
        await self.db.commit()
        return user_in_db


def get_user_crud(db=Depends(get_session)) -> UserCrud:
    return UserCrud(db=db)
