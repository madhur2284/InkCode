from database import get_db
from models.db_models import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from typing import Optional
from sqlalchemy import select

async def get_user_by_username(username: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    return user 

async def get_user_by_email(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    return user

async def get_user_by_id_token_version(id: int, token_version: int,db: AsyncSession):
    result = await db.execute(select(User).where(User.id == id, User.is_active == True, User.token_version == token_version))
    user = result.scalar_one_or_none()
    return user

async def add_user(email: str, username: str, bio: Optional[str], hashed_password: str, avatar_url: str,avatar_public_id: str, db: AsyncSession, slug: str):
    user = User(username=username, email=email, hashed_password=hashed_password, bio=bio, avatar_url=avatar_url, avatar_post_id=avatar_public_id,slug=slug)
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add user in database")