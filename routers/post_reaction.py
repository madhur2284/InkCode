from fastapi import APIRouter, status, HTTPException, Depends, Path
from schemas.post_reaction import PostReactionCreate
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.auth import get_current_user
from crud.post_reaction import create_post_reaction, delete_reaction

router = APIRouter(prefix="/post_reaction", tags=["post_reaction"])

@router.post(path='/', status_code=status.HTTP_201_CREATED)
async def add_reaction(reaction_detail: PostReactionCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)) -> str:
    try:
        message = await create_post_reaction(db, reaction_detail.post_id, current_user.id, reaction_detail.type)
        return message.get("Message", "")
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")
    

@router.delete(path='/{post_id}', status_code=status.HTTP_200_OK)
async def remove_reaction(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), post_id: int = Path(description="Post ID", gt=0))->str:
    result = await delete_reaction(post_id, db, current_user.id)
    return result.get("message", "")