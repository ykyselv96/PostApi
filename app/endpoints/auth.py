from fastapi import APIRouter, status, Depends
from core.connections import get_session
from schemas.user_schema import UsersResponse, SignInForm, SignupForm
from jose import jwt
from datetime import datetime, timedelta
from core.config import system_config
import math
from crud.user_crud import UserCrud, get_user_crud
from fastapi.security import HTTPBearer

from crud.user_crud import get_user_crud

# from core.get_current_user import get_current_user

from core.get_current_user import get_current_user


router = APIRouter(tags=["authorization and registration"], prefix="/users")

token_auth_scheme = HTTPBearer()


def create_access_token(user_email) -> str:

    expires_delta = datetime.utcnow() + timedelta(minutes=int(system_config.settings.access_token_expire_minutes))

    to_encode = {"exp": expires_delta, "sub": str(user_email)}
    encoded_jwt = jwt.encode(to_encode, system_config.settings.jwt_access_secret_key, system_config.settings.algorithm)

    return encoded_jwt


def create_refresh_token(user_email) -> str:

    refresh_token_expire_minutes = math.prod([int(el) for el in system_config.settings.refresh_token_expire_minutes.split('*')])

    expires_delta = datetime.utcnow() + timedelta(minutes=int(refresh_token_expire_minutes))

    to_encode = {"exp": expires_delta, "sub": str(user_email)}
    encoded_jwt = jwt.encode(to_encode, system_config.settings.jwt_refresh_secret_key, system_config.settings.algorithm)
    return encoded_jwt


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(payload: SignInForm, db=Depends(get_session)):

    user_crud = UserCrud(db=db)
    user_in_db = await user_crud.get_user_by_email_and_password(email=payload.email, password=payload.password)

    return {
        "token_type": 'Bearer',
        "access_token": create_access_token(user_in_db.email),
        "refresh_token": create_refresh_token(user_in_db.email),
    }


@router.post("/", status_code=status.HTTP_200_OK, response_model=UsersResponse)
async def add_new_user(payload: SignupForm, user_crud: UserCrud = Depends(get_user_crud)) -> UsersResponse:
    res = await user_crud.create_user(payload=payload)
    return res


@router.get("/me", status_code=status.HTTP_200_OK)
async def me(current_user=Depends(get_current_user)) -> UsersResponse:
    return current_user
