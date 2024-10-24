from pydantic import BaseModel, Field, root_validator
from typing import Optional, Any

from fastapi import HTTPException, status

from utils.hash_password import hash_password


class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    comments_reply: Optional[bool] = False
    auto_reply_delay: Optional[int] = 0

class UsersResponse(BaseModel):
    id: int
    username: str
    email: str
    comments_reply: Optional[bool] = False
    auto_reply_delay: Optional[int] = 0

    class Config:
        orm_mode = True

class SignInForm(BaseModel):
    email: str
    password: str


class SignupForm(BaseModel):
    username: str
    email: str
    password: str = Field(..., min_length=8)
    password_repeat: str = Field(..., min_length=8)
    comments_reply: Optional[bool] = False
    auto_reply_delay: Optional[int] = 0

    @root_validator  # type: ignore
    def validate_password(cls, model_values: dict[Any, Any]) -> dict[Any, Any]:
        password = model_values.get('password')
        password_repeat = model_values.get('password_repeat')

        email = model_values.get('email')

        if not email:
            raise HTTPException(
                detail="Please provide a valid email.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        emails_ex = ['@', 'gmail.com', '@ukr.net', 'mail.ru', 'yandex.ru']

        for el in emails_ex:
            if el in email:
                model_values['email'] = email
                break
            else:
                raise HTTPException(
                    detail="Please provide a valid email.",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

        if not password:
            raise HTTPException(
                detail="Password must contain at least 8 characters",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if password != password_repeat:
            raise HTTPException(
                detail="Passwords do not match",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        hashed_password = hash_password(password)
        model_values['password'] = hashed_password

        return model_values
