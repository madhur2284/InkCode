from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.db_models import Bookmark
from fastapi import HTTPException, status

async def add_bookmark(user_id: int, post_id: int, db: AsyncSession):
    resut = await db.execute(select(Bookmark).where(Bookmark.post_id == post_id, Bookmark.user_id == user_id))
    bookmark = resut.scalar_one_or_none()
    if bookmark:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bookmark already exist")
    
    post_bookmark = Bookmark(post_id = post_id, user_id = user_id)
    try:
        db.add(post_bookmark)
        await db.commit()
        return {"message": "Bookmark is created"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    

async def delete_bookmark(user_id:int, post_id: int, db: AsyncSession):
    result = await db.execute(select(Bookmark).where(Bookmark.post_id == post_id, Bookmark.user_id == user_id))
    bookmark = result.scalar_one_or_none()

    if not bookmark:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bookmark didn't exist")
    
    try:
        await db.delete(bookmark)
        await db.commit()
        return {"message": "Bookmark deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")