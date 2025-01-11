from fastapi import APIRouter, Depends, UploadFile

from starlette import status

from starlette.requests import Request
from starlette.responses import Response

from app.auth.utils import get_access_token, get_refresh_token
from app.repositories.user_repository import get_user_repository, UserRepository
from app.users.schemas import UserCreate, UserLogin
user_router = APIRouter(prefix="/users", tags=["USERS"])





@user_router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user( resp: Response, user: UserCreate, session: UserRepository = Depends(get_user_repository)):
    return await session.create_user(user, resp)


@user_router.post("/login")
async def login(user: UserLogin, response: Response, request: Request, session: UserRepository = Depends(get_user_repository)):
    return await session.login_user(user, response, request)


# @user_router.post("/refresh")
# async def refresh_jwt(response: Response, data: TokenRefresh, session: UserRepository = Depends(get_repository)):
#     return await session.refresh_token(response, data)

@user_router.post("/action")
async def get_me(response: Response, session: UserRepository = Depends(get_user_repository), access_data: dict | bool = Depends(get_access_token), refresh_data: dict | bool = Depends(get_refresh_token)):
    return await session.refresh(response, access_data, refresh_data)


@user_router.post("/logout")
async def sign_out(resp: Response,  refresh_data: dict | bool = Depends(get_refresh_token), session: UserRepository = Depends(get_user_repository)):
    return await session.log_out(resp, refresh_data)

@user_router.post("/upload_ava", status_code=status.HTTP_201_CREATED)
async def upload_ava(file: UploadFile, access_data: bool | dict = Depends(get_access_token), session: UserRepository = Depends(get_user_repository)):
    return await session.create_upload_file(file, access_data)

@user_router.get("/avatar/{filename}")
async def get_avatar(filename: str, session: UserRepository = Depends(get_user_repository)):
    return await session.serve_avatar(filename)

@user_router.get("/give_rights/{nickname}")
async def give_rights(nickname: str, session: UserRepository = Depends(get_user_repository)):
    return await session.delegate_rights_to_user(nickname)


@user_router.get("/take_rights/{nickname}")
async def take_rights(nickname: str, session: UserRepository = Depends(get_user_repository)):
    return await session.take_rights_from_user(nickname)

@user_router.get("/current_user")
async def current_user(session: UserRepository = Depends(get_user_repository), access_data: dict | bool = Depends(get_access_token)):
    return await session.get_user_by_id(access_data)


@user_router.get("/delete_ava")
async def remove_ava(session: UserRepository = Depends(get_user_repository), access_data: dict | bool = Depends(get_access_token)):
    return await session.remove_avatar(access_data)

