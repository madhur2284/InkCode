import asyncio
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from config import settings
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.db_models import User


context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized")

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    result = await db.execute(select(User).where(User.id == payload.get("id"), User.is_active == True, User.token_version == payload.get("token_version")))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHORIZED")
    
    return user


async def get_optional_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User | None:
    if not token:
        return None
    try:
        payload = decode_token(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unuthorized")

    if not payload:
        return None
    
    result = await db.execute(select(User).where(User.id == payload.get("id"), User.is_active == True, User.token_version == payload.get("token_version")))
    current_user = result.scalar_one_or_none()
    
    return current_user

    
async def require_admin(user: User = Depends(get_current_user)):

    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin")
    return user


async def hash_password(password) -> str:
    """Conver plain password into hashed password"""
    hashed_password = await asyncio.to_thread(context.hash, password)
    return hashed_password

async def verify_password(plain_password, hash_password) -> bool:
    """Return true if plain_password hash is equal to the given hash otherwise false"""
    result = await asyncio.to_thread(context.verify, plain_password, hash_password)
    return result

def decode_token(token: str) -> dict:
    """Decode the JWT Token and return the payload"""
    payload = jwt.decode(
        token=token,
        key=settings().SECRET_KEY,
        algorithms=["HS256"]
    )
    return payload

def generate_access_token(payload: dict) -> str:
    """Encode the payload and return the jwt token. Minimum  info required {"id": 1, "role": "user", "token_version": 1}"""
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    to_encode["type"] = "access_token"
    token = jwt.encode(
        to_encode,
        key=settings().SECRET_KEY,
        algorithm="HS256"
    )
    return token


def generate_refresh_token(payload: dict) -> str:
    """Encode the payload and return the jwt token. Minimum  info required {"id": 1, "role": "user", "token_version": 1}"""
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings().REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode["exp"] = expire
    to_encode["type"] = "refresh"
    token = jwt.encode(
        to_encode,
        key=settings().SECRET_KEY,
        algorithm="HS256"
    )
    return token