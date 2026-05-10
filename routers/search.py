from fastapi import APIRouter, Path, Query, status, Depends, HTTPException
from models.db_models import Post
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.search import SearchResponse
from services.auth import get_optional_current_user
from crud.search import get_posts


router = APIRouter(prefix='/search', tags=["search"])

@router.get(path='/', status_code=status.HTTP_200_OK, response_model=SearchResponse)
async def get_posts_by_search(db: AsyncSession = Depends(get_db), current_user = Depends(get_optional_current_user),query: str = Query(description="search query"), limit: int = Query(description="limit of response per page", default=10, gt=0), page: int = Query(description="Current Page Number", default=1, gt=0)):
    if not query or not query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"query is blank")
    
    user_id = 0
    if current_user:
        user_id = current_user.id

    result = await get_posts(db, query, limit, page, user_id)
    return result
    
