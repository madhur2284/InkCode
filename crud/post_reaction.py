from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import Reaction
from sqlalchemy import select
from fastapi import HTTPException, status

async def create_post_reaction(db: AsyncSession, post_id: int, user_id: int, type: str):
    result = await db.execute(select(Reaction).where(Reaction.post_id == post_id, Reaction.user_id == user_id))
    reaction = result.scalar_one_or_none()
    if reaction:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Reaction already exist")
    
    post_reaction = Reaction(post_id = post_id, user_id = user_id, type = type)

    try:
        db.add(post_reaction)
        await db.commit()
        return {"Message": "Reaction added successfully"}
    except:
        await db.rollback()
        raise ValueError(f"Failed to add Reaction")
    

async def delete_reaction(post_id:int, db: AsyncSession, user_id: int):
    result =   await db.execute(select(Reaction).where(Reaction.post_id == post_id, Reaction.user_id == user_id))
    reaction = result.scalar_one_or_none()

    if not reaction:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail=f"No Reaction found")
    
    try:
        await db.delete(reaction)
        await db.commit()
        return {"message": "Reaction Deleted Successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    
