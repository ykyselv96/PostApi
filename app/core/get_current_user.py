from fastapi import Depends, Request
from crud.user_crud import User, get_user_crud, UserCrud
from schemas.user_schema import User
from core.connections import get_session
from fastapi.security import HTTPBearer
from utils.verify_token import VerifyToken
from fastapi import status, HTTPException


token_auth_scheme = HTTPBearer()


async def get_current_user(request: Request, db=Depends(get_session), token: str = Depends(token_auth_scheme)) -> User:

    user_crud = UserCrud(db=db)

    result = VerifyToken(token.credentials).verify()

    if result.get("status"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("message"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    else:
        resp = await user_crud.get_user_by_email(email=result.get('sub'))
        return resp
