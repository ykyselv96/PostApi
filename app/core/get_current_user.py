from fastapi import Depends, Request,  status, HTTPException
from fastapi.security import HTTPBearer
from crud.user_crud import UserCrud
from schemas.user_schema import User
from core.connections import get_session
from utils.verify_token import VerifyToken


token_auth_scheme = HTTPBearer()


async def get_current_user(request: Request, db=Depends(get_session), token: str = Depends(token_auth_scheme)) -> User:
    """Retrieve the currently authenticated user from the database.

     This function checks the validity of the provided JWT token, extracts the
     user information from it, and returns the corresponding user from the database.

     Parameters:
         request (Request): The incoming HTTP request.
         db (AsyncSession): The database session dependency, automatically provided
                            by FastAPI.
         token (str): The JWT token extracted from the request, obtained using the
                      `token_auth_scheme`.

     Returns:
         User: The authenticated user object retrieved from the database.

     Raises:
         HTTPException: If the token is invalid or expired, a 401 Unauthorized
                        exception is raised with an appropriate error message.
     """
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
