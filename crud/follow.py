from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.db_models import Follow, User, Notification
from services.notification import initiate_notification
from fastapi import HTTPException, status

async def create_follow(db: AsyncSession, follower_id: int, following_id: int) -> dict[str, str]:
    result = await db.execute(select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id))
    follow = result.scalar_one_or_none()

    if follow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Follow Record already exist")
    
    result = await db.execute(select(User).where(User.id == following_id, User.is_active==True))
    following = result.scalar_one_or_none()

    if not following:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No user exist with id: {following_id}")

    user_follow = Follow(follower_id = follower_id, following_id = following_id)
    try:
        db.add(user_follow)
        await db.commit()
        return {"message": "Follow Record Successfully Created"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    

async def delete_follow(db: AsyncSession, follower_id: int, following_id: int) -> dict[str, str]:
    result = await db.execute(select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id))
    follow = result.scalar_one_or_none()

    if not follow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Follow Record didn't exist")
    
    try:
        await db.delete(follow)
        await db.commit()
        return {"message": "Follow Record successfully Deleted"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    

async def create_follow_notification(db: AsyncSession, follower_id: int, following_id: int, avatar_url: str, username: str):
    notify = Notification(type="follow", actor_id=follower_id, recipient_id=following_id)
    db.add(notify)
    await db.commit()
    await db.refresh(notify)
    await initiate_notification(notify.recipient_id, {"notification_id": str(notify.id), "type": notify.type, "avatar_url": avatar_url, "username": username, "user_id": follower_id, "content": following_id, "message": f"{username} followed you"})
    