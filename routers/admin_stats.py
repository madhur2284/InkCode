from fastapi import APIRouter, status, Depends
from schemas.admin_stats import StatResponse
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth import require_admin
from database import get_db
from crud.admin_stats import get_stats


router = APIRouter(prefix="/admin_stats", tags=["admin_stats"])

@router.get(path='/', status_code=status.HTTP_200_OK, response_model=StatResponse)
async def get_admin_stat(db: AsyncSession = Depends(get_db), admin = Depends(require_admin)):
    stats = await get_stats(db)
    return stats