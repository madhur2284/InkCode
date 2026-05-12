from fastapi import APIRouter, status, Depends, HTTPException, Path
from schemas.tag import TagCreate, TagResposne
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth import require_admin, get_current_user
from database import get_db
from models.db_models import User, Tag
from crud.tag import get_tag_by_name, add_tag, delete_tag_by_slug
from services.slug import create_unique_slug


router = APIRouter(prefix="/tag", tags=["tag"])

@router.post(path='/', status_code=status.HTTP_201_CREATED, response_model=TagResposne)
async def create_tag(tag: TagCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_user)):
    existing_tag = await get_tag_by_name(tag.name, db)
    
    if existing_tag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tag with this name already exist")

    slug = await create_unique_slug(tag.name, db, Tag)
    
    try: 
        new_tag = await add_tag(tag.name, slug, tag.description, db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    
    return new_tag


@router.delete(path='/{slug}', status_code=status.HTTP_200_OK)
async def delete_tag(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin), slug: str = Path(description="slug of tag")):
    try:
        await delete_tag_by_slug(slug, db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")
    
    return {"message": "Tag deleted successfully"}
