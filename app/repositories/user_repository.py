import os
import uuid
from abc import ABC, abstractmethod

from fastapi import Depends, HTTPException, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from app.auth.utils import validate_password, hash_password, verify_password, create_access_token, create_refresh_token, \
    get_access_token, get_refresh_token
from app.database.config import get_async_session, settings
from app.database.models import User, Idea
from app.users.schemas import UserCreate, UserLogin


async def get_user_repository(session: AsyncSession = Depends(get_async_session)):
    return UserRepository(session)


class AbstractUserRepository(ABC):

    @abstractmethod
    async def create_user(self, payload: UserCreate, response: Response):
        raise NotImplementedError

    @abstractmethod
    async def login_user(self, creds: UserLogin, response: Response, request: Request):
        raise NotImplementedError

    @abstractmethod
    async def refresh(self, response: Response, access_data: str | bool = Depends(get_access_token),
                      refresh_dats: dict | bool = Depends(get_refresh_token)):
        raise NotImplementedError

    @abstractmethod
    async def log_out(self, resp: Response, refresh_data: dict | bool = Depends(get_refresh_token)):
        raise NotImplementedError

    @abstractmethod
    async def delegate_rights_to_user(self, nickname: str):
        raise NotImplementedError

    @abstractmethod
    async def take_rights_from_user(self, nickname: str):
        raise NotImplementedError

    @abstractmethod
    async def count_ideas(self, access_data: str | bool = Depends(get_access_token)):
        raise NotImplementedError

    @abstractmethod
    async def create_upload_file(self, file: UploadFile = File(...)):
        raise NotImplementedError


class UserRepository(AbstractUserRepository):
    REFRESH_TOKEN_TIME = settings.REFRESH_TOKEN_EXPIRES_IN
    ACCESS_TOKEN_TIME = settings.ACCESS_TOKEN_EXPIRES_IN
    SECRET_ACCESS_KEY = settings.PRIVATE_ACCESS_KEY
    SECRET_REFRESH_KEY = settings.PRIVATE_REFRESH_KEY
    ALGORITHM = settings.JWT_ALGORITHM
    UPLOAD_FOLDER = "uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, access_data: dict | bool = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log in to continue")
        user = await self.session.execute(select(User).filter(User.id == access_data["user_id"]))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't exist"
            )
        return user

    async def get_user_by_avatar(self, filename: str):
        user = await self.session.execute(select(User).filter(User.avatar_filename == filename))
        return user.scalar_one_or_none()

    async def remove_avatar(self, access_data: dict | bool = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sign in to continue"
            )
        try:
            user = await self.session.execute(select(User).filter(User.avatar_filename == access_data["ava_filename"]))
            user = user.scalar_one_or_none()
            if user:
                user.avatar_filename = "none"
                self.session.add(user)
                await self.session.commit()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error": e})

    async def create_user(self, payload: UserCreate, response: Response):
        user = await self.session.execute(select(User).filter(User.email == payload.email))
        user = user.scalar_one_or_none()
        if user:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="The user already exists")
        # Compare password and passwordConfirm
        if payload.password != payload.passwordConfirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

        if not validate_password(payload.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Password must be > 8, contain at least one uppercase letter and must contain one lowercase letter')
        try:
            user_id = str(uuid.uuid4())
            #  Hash the password
            jwt_payload_access = {
                "id": user_id,
                "nickname": payload.nickname,
                "ava_filename": "none"
            }
            jwt_payload_refresh = {
                "id": user_id,
                "nickname": payload.nickname,
                "name": payload.first_name,
                "email": payload.email,
                "role": jsonable_encoder(payload.role),
                "password": payload.password
            }
            payload.password = hash_password(payload.password)
            payload.id = user_id
            payload.role = "user"

            del payload.passwordConfirm
            payload.email = payload.email.lower()
            access_token = create_access_token(jwt_payload_access)  # secret_key=settings.JWT_PRIVATE_KEY
            refresh_token = create_refresh_token(jwt_payload_refresh)
            to_add = User(**payload.model_dump())
            self.session.add(to_add)
            await self.session.commit()
            await self.session.refresh(to_add)
            response.set_cookie("access_token", access_token, max_age=self.ACCESS_TOKEN_TIME * 60, path="/",
                                httponly=True, samesite="lax")
            response.set_cookie("refresh_token", refresh_token, max_age=self.REFRESH_TOKEN_TIME * 60, path="/",
                                httponly=True, samesite="lax")

            return f"Welcome aboard, {to_add.first_name} {to_add.last_name}!"
        except Exception as e:
            error = type(e).__name__
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"Error": error, "full details": e.__str__()}
                                )

    async def login_user(self, creds: UserLogin, response: Response, request: Request):
        if not creds:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid credentials")
        if request.cookies.get('access_token'):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="You've already logged in"
            )
        user = await self.session.execute(select(User).filter(User.email == creds.email))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't exist"
            )
        if not verify_password(creds.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
            )

        jwt_payload_access = {
            "id": jsonable_encoder(user.id),
            "nickname": user.nickname,
            "ava_filename": jsonable_encoder(user.avatar_filename)
        }
        jwt_payload_refresh = {
            "id": jsonable_encoder(user.id),
            "nickname": user.nickname,
            "name": user.first_name,
            "email": user.email,
            "role": jsonable_encoder(user.role),
            "password": jsonable_encoder(user.password)
        }
        access_token = create_access_token(jwt_payload_access)  # secret_key=settings.JWT_PRIVATE_KEY
        refresh_token = create_refresh_token(jwt_payload_refresh)

        response.set_cookie("access_token", access_token, max_age=self.ACCESS_TOKEN_TIME * 60, path="/", httponly=True,
                            samesite="lax")
        response.set_cookie("refresh_token", refresh_token, max_age=self.REFRESH_TOKEN_TIME * 60, path="/",
                            httponly=True,
                            samesite="lax")
        return {"status": f"Welcome back, {user.nickname}!", "access_token": access_token}

    async def create_upload_file(self, file: UploadFile = File(...),
                                 access_data: bool | dict = Depends(get_access_token)):
        if not access_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sign in to continue"
            )
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not specified"
            )

        max_file_size_mb = 10
        max_file_size_bytes = max_file_size_mb * 1024 * 1024

        if file.size > max_file_size_bytes:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
            # Получение типа MIME
        content_type = file.content_type
        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/gif",  # Или другие типы изображений
        }

        if content_type not in allowed_types:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type")

        try:

            unique_filename = str(uuid.uuid4()) + file.filename.split(".")[-1]
            filepath = os.path.join(self.UPLOAD_FOLDER, unique_filename)
            with open(filepath, "wb") as f:
                content = await file.read()
                f.write(content)

            user = await self.session.execute(select(User).filter(User.id == access_data["user_id"]))
            user = user.scalar_one_or_none()
            await self.session.execute(update(User).filter(User.id == user.id).values(avatar_filename=unique_filename))
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            return JSONResponse({"message": f"Loading error: {e}"}, status_code=500)
        return JSONResponse({"filename": unique_filename})

    async def serve_avatar(self, filename: str):
        filepath = os.path.join(self.UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            if await self.get_user_by_avatar(filename):
                return StreamingResponse(
                    (open(filepath, "rb")),
                    media_type="image/",  # Crucial!
                    headers={"Content-Disposition": f"inline; filename={filename}"},
                )
            else:
                return HTTPException(status_code=404,
                                     detail="File not found or avatar no longer associated with any user.")

    async def refresh(self, response: Response, access_data: dict | bool = Depends(get_access_token),
                      refresh_data: dict | bool = Depends(get_refresh_token)):
        if not refresh_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Log in to continue")
        user = await self.session.get(User, refresh_data["user_id"])
        if not access_data:
            jwt_payload_access = {
                "id": jsonable_encoder(user.id),
                "nickname": user.nickname,
            }
            jwt_payload_refresh = {
                "id": jsonable_encoder(user.id),
                "nickname": user.nickname,
                "role": jsonable_encoder(user.role),
            }

            access_token = create_access_token(jwt_payload_access)
            refresh_token = create_refresh_token(jwt_payload_refresh)
            response.set_cookie("access_token", access_token, max_age=self.ACCESS_TOKEN_TIME * 60, path="/",
                                httponly=True,
                                samesite="lax")
            response.set_cookie("refresh_token", refresh_token, max_age=self.REFRESH_TOKEN_TIME * 60, path="/",
                                httponly=True,
                                samesite="lax")
            return {"message": "tokens have been updated"}

        return {"message": "Successfully redirected"}

    async def log_out(self, resp: Response, refresh_data: dict | bool = Depends(get_refresh_token)):
        if not refresh_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You have to log in to log out =)"
            )

        try:
            resp.delete_cookie("access_token", path="/")
            resp.delete_cookie("refresh_token", path="/")
            return {"status": "logged out successfully"}
        except Exception as e:
            await self.session.rollback()
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e.__str__())

    async def delegate_rights_to_user(self, nickname: str):
        try:
            await self.session.execute(update(User).filter(User.nickname == nickname).values(role="admin"))
            await self.session.commit()
            return {"status": f"user {nickname} is the admin now"}
        except Exception as e:
            await self.session.rollback()
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e.__str__())

    async def take_rights_from_user(self, nickname: str):
        try:
            await self.session.execute(update(User).where(User.nickname == nickname).values(role="user"))
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e.__str__())
        return {"status": f"admin panel is taken from user {nickname}"}

    async def count_ideas(self, access_data: dict | bool = Depends(get_access_token)):
        try:
            res = await self.session.execute(select(Idea).filter(Idea.user_id == access_data["user_id"]))
            ideas = res.scalars().all()
            return len(ideas)
        except Exception as e:
            return f"Error while counting ideas: {e}"
