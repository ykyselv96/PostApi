from datetime import datetime
from typing import List, Optional

from pydantic import ValidationError

from core.config import system_config
from core.connections import get_session
from db.models import User
from sqlalchemy import select, insert, update, delete
from fastapi import status, HTTPException, Request, Depends, Request
from schemas.user_schema import UsersResponse, SignupForm

from jose import jwt
from schemas.user_schema import UsersResponse
import requests
from utils.hash_password import check_password, hash_password


class UserCrud:
    def __init__(self, db):
        self.db = db

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
        statement = select(User).where(User.email==email)
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


def get_user_crud(db=Depends(get_session)) -> UserCrud:
    return UserCrud(db=db)
