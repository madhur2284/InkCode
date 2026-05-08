from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import CommentReaction
from sqlalchemy import select
from fastapi import HTTPException, status

async def create_comment_reaction(db: AsyncSession, comment_id: int, user_id: int, type: str):
    result =   await db.execute(select(CommentReaction).where(CommentReaction.comment_id == comment_id, CommentReaction.user_id == user_id))
    reaction = result.scalar_one_or_none()
    if reaction:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Reaction already exist")
    comment_reaction = CommentReaction(comment_id = comment_id, user_id = user_id, type = type)
    try:
        db.add(comment_reaction)
        await db.commit()
        return {"Message": "Reaction added successfully"}
    except:
        await db.rollback()
        raise ValueError(f"Failed to add Reaction")
    

async def delete_reaction(comment_id:int, db: AsyncSession, user_id: int):
    result =   await db.execute(select(CommentReaction).where(CommentReaction.comment_id == comment_id, CommentReaction.user_id == user_id))
    reaction = result.scalar()
    if not reaction:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail=f"No Reaction found")
    
    try:
        await db.delete(reaction)
        await db.commit()
        return {"message": "Reaction Deleted Successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    
