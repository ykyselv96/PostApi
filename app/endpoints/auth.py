from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import HTTPBearer
from core.connections import get_session
from crud.user_crud import UserCrud, get_user_crud
from core.get_current_user import get_current_user
from schemas.user_schema import UsersResponse, SignInForm, SignupForm, UserUpdateForm
from fastapi_pagination import Page, Params, paginate


router = APIRouter(tags=["authorization and registration"], prefix="/users")

token_auth_scheme = HTTPBearer()


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(payload: SignInForm, db=Depends(get_session)):

    user_crud = UserCrud(db=db)
    user_in_db = await user_crud.get_user_by_email_and_password(email=payload.email, password=payload.password)

    return {
        "token_type": 'Bearer',
        "access_token": user_crud.create_access_token(user_in_db.email),
        "refresh_token": user_crud.create_refresh_token(user_in_db.email),
    }


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UsersResponse)
async def create_user(payload: SignupForm, user_crud: UserCrud = Depends(get_user_crud)) -> UsersResponse:
    res = await user_crud.create_user(payload=payload)
    return res


@router.get("/", status_code=status.HTTP_200_OK, response_model=Page[UsersResponse])
async def get_all_users(user_crud: UserCrud = Depends(get_user_crud), params: Params = Depends()) \
        -> Page[UsersResponse]:
    res = await user_crud.get_all_users()
    return paginate(res, params)


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UsersResponse)
async def get_user_by_id(user_id: int, user_crud: UserCrud = Depends(get_user_crud)) -> UsersResponse:
    return await user_crud.get_user_by_id(user_id=user_id)


@router.delete("/{user_id}",  status_code=status.HTTP_200_OK, response_model=UsersResponse)
async def delete_user(user_id: int, user_crud: UserCrud = Depends(get_user_crud),
                      curr_user=Depends(get_current_user)) -> UsersResponse:

    if curr_user.id == user_id:
        return await user_crud.delete_user(user_id=user_id)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't delete another users",
        )


@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=UsersResponse)
async def update_user(payload: UserUpdateForm, user_id: int, user_crud: UserCrud = Depends(get_user_crud),
                      curr_user=Depends(get_current_user)) -> UsersResponse:

    if curr_user.id == user_id:
        res = await user_crud.update_user(payload=payload, user_id=user_id)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't update other users",
        )

    return res


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UsersResponse)
async def me(current_user=Depends(get_current_user)) -> UsersResponse:
    return current_user
