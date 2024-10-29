from pydantic import BaseModel, Field, root_validator
from typing import Optional, Any
from fastapi import HTTPException, status
from utils.hash_password import hash_password


class User(BaseModel):
    """Model representing a user in the system.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The hashed password of the user.
        comments_reply (Optional[bool]): Indicates if the user want to have auto_reply to comments (default is False).
        auto_reply_delay (Optional[int]): The delay in minutes for automatic replies (default is 0).
    """
    id: int
    username: str
    email: str
    password: str
    comments_reply: Optional[bool] = False
    auto_reply_delay: Optional[int] = 0


class UsersResponse(BaseModel):
    """Model representing a user response(how it shown to other users).

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        comments_reply (Optional[bool]): Indicates if the user want to have auto_reply to comments (default is False).
        auto_reply_delay (Optional[int]): The delay in minutes for automatic replies (default is 0).
    """
    id: int
    username: str
    email: str
    comments_reply: Optional[bool] = False
    auto_reply_delay: Optional[int] = 0

    class Config:
        orm_mode = True


class SignInForm(BaseModel):
    """Model for user sign-in(login).

    Attributes:
        email (str): The email address of the user.
        password (str): The password of the user.
    """
    email: str
    password: str


class UserUpdateForm(BaseModel):
    """Model for user update.

       Attributes:
           username (Optional[str]): The desired username of the user.
           email (Optional[str]): The email address of the user.
           password (Optional[str]): The password of the user (must be at least 8 characters).
           password_repeat (Optional[str]): A repeat of the password for confirmation (must match the password).
           comments_reply (Optional[bool]): Indicates if the user want to have auto_reply to comments
           (default is False).
           auto_reply_delay (Optional[int]): The delay in minutes for automatic replies (default is 0).
       """
    username: Optional[str]
    email: Optional[str]
    password: Optional[str] = Field(None, min_length=8)
    password_repeat: Optional[str] = Field(None, min_length=8)
    comments_reply: Optional[bool] = False
    auto_reply_delay: Optional[int] = 0

    @root_validator  # type: ignore
    def validate_password_and_email(cls, model_values: dict[Any, Any]) -> dict[Any, Any]:
        """
        Validates the password and email fields during user update.

        Checks if the password meets the minimum length requirement,
        ensures that both password fields match, and verifies that the email is valid.

        Args:
            cls: The class being validated.
            model_values (dict): The values of the model attributes.

        Returns:
            dict: The validated model values, with the hashed password.

        Raises:
            HTTPException: If any validation fails with appropriate error messages.
        """
        password = model_values.get('password')
        password_repeat = model_values.get('password_repeat')

        email = model_values.get('email')

        if email is not None:

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

        if password is not None:
            if password_repeat is None or password != password_repeat:
                raise HTTPException(
                    detail="Passwords do not match",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            hashed_password = hash_password(password)
            model_values['password'] = hashed_password

        return model_values


class SignupForm(BaseModel):
    """Model for user signup.

    Attributes:
        username (str): The desired username of the user.
        email (str): The email address of the user.
        password (str): The password of the user (must be at least 8 characters).
        password_repeat (str): A repeat of the password for confirmation (must match the password).
        comments_reply (Optional[bool]): Indicates if the user want to have auto_reply to comments (default is False).
        auto_reply_delay (Optional[int]): The delay in minutes for automatic replies (default is 0).
    """
    username: str
    email: str
    password: str = Field(..., min_length=8)
    password_repeat: str = Field(..., min_length=8)
    comments_reply: Optional[bool] = False
    auto_reply_delay: Optional[int] = 0

    @root_validator  # type: ignore
    def validate_password_and_email(cls, model_values: dict[Any, Any]) -> dict[Any, Any]:
        """
        Validates the password and email fields during user signup.

        Checks if the password meets the minimum length requirement,
        ensures that both password fields match, and verifies that the email is valid.

        Args:
            cls: The class being validated.
            model_values (dict): The values of the model attributes.

        Returns:
            dict: The validated model values, with the hashed password.

        Raises:
            HTTPException: If any validation fails with appropriate error messages.
        """
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
