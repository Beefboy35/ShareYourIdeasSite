import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    MODER = "moder"

class UserBase(BaseModel):
    id: str = "123"
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(UserBase):
    nickname: str = Field("Enter your nickname")
    password: str
    passwordConfirm: str
    role: str = "user"
    avatar_filename: str = "none"



class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenRefresh(BaseModel):
    id: str
    password: str
    nickname: str
