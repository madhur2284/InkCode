from fastapi import APIRouter, status, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.auth import get_current_user
from crud.bookmark import add_bookmark, delete_bookmark

router = APIRouter(prefix="/bookmark", tags=["bookmark"])

@router.post(path='/{post_id}', status_code=status.HTTP_201_CREATED)
async def create_bookmark(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), post_id: int = Path(description="Post ID", gt=0)):
    result = await add_bookmark(current_user.id, post_id, db)
    return result.get("message")


@router.delete(path='/{post_id}', status_code=status.HTTP_200_OK)
async def remove_bookmark(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), post_id: int = Path(description="Post ID", gt=0)):
    result = await delete_bookmark(current_user.id, post_id, db)
    return result.get("message")