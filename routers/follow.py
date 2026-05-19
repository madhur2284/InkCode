from fastapi import APIRouter, status, Depends, Path
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth import get_current_user
from crud.follow import create_follow, delete_follow, create_follow_notification

router = APIRouter(prefix="/follow", tags=["follow"])

@router.post(path='/{following_id}', status_code=status.HTTP_201_CREATED)
async def add_follow(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), following_id: int = Path(description="Following ID")) -> str:
    result = await create_follow(db, current_user.id, following_id)
    await create_follow_notification(db, current_user.id, following_id, current_user.avatar_url, current_user.username)
    return result.get("message", "")


@router.delete(path='/{following_id}', status_code=status.HTTP_200_OK)
async def remove_follow(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), following_id: int = Path(description="Following ID", gt=0)) -> str:
    result = await delete_follow(db, current_user.id, following_id)
    return result.get("message", "")