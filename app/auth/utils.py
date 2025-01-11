import re

from fastapi import HTTPException
from jose import JWTError
from jose.jwt import encode, decode

from passlib.context import CryptContext

from starlette import status
from starlette.requests import Request


from app.database.config import settings



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def validate_password(password):
    # More complex password validation.  Example includes length check and basic complexity.
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
SECRET_ACCESS_KEY = settings.PRIVATE_ACCESS_KEY
SECRET_REFRESH_KEY = settings.PRIVATE_REFRESH_KEY
ALGORITHM = settings.JWT_ALGORITHM
def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = encode(to_encode, key=SECRET_ACCESS_KEY, algorithm=ALGORITHM, headers={"Authorization": "Bearer"})
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = encode(to_encode, key=SECRET_REFRESH_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def get_access_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return False
    try:
        payload = decode(token, SECRET_ACCESS_KEY, algorithms=ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not valid")

    user_id = payload.get("id")
    nickname = payload.get("nickname")
    ava_filename = payload.get("ava_filename")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = {"user_id": str(user_id), "nickname": nickname, "ava_filename": str(ava_filename)}
    return result


async def get_refresh_token(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        return False
    try:
        payload = decode(token, SECRET_REFRESH_KEY, algorithms=ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not valid")
    user_id = payload.get("id")
    nickname = payload.get("nickname")
    email =  payload.get("email")
    role = payload.get("role")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = {"user_id": str(user_id), "nickname": nickname, "email": email, "role": role}
    return result








#async def delete_expired_refresh_tokens(db: AsyncSession):
#    """Deletes expired refresh tokens from the database."""
#    try:
#        now = func.now()
#        await db.execute(
#            update(User)
#            .where(User.expires_at < now)
#            .values(is_logged_in=False, refresh_token="None"))  # Set token to 'None', and updates expires_at
#        await db.commit()
 #   except Exception as e:
#        print(f"Error deleting expired tokens: {e}")
#        await db.rollback()