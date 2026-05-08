from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import math
from fastapi import HTTPException, status

async def pagination_calculate(db: AsyncSession, page: int, limit: int, model) -> dict:
    result = await db.execute(select(func.count()).where(model.is_active == True))
    total_rows = result.scalar()
    total_pages = math.ceil(total_rows/limit)
    if page > total_pages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Max Page Count is only {total_pages}")
    
    skip_count = (page-1)*limit

    return{
        "total_pages": total_pages,
        "skip": skip_count
    }

