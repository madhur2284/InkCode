from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import Reaction, Notification, Post
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from services.notification import initiate_notification

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add Reaction")
    

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
    
async def post_reaction_notification(db: AsyncSession, avatar_url: str, username: str, user_id, post_id, type: str):
    result = await db.execute(select(Post).where(Post.id == post_id, Post.is_active==True, Post.status == 'published'))
    post = result.scalar_one_or_none()
    
    if user_id == post.author_id:
        return
    notify = Notification(type="post_like" if type=='like' else "post_dislike", actor_id=user_id, recipient_id= post.author_id, post_id=post_id)
  
    db.add(notify)      
    await db.commit()
    await db.refresh(notify)
    await initiate_notification(notify.recipient_id, {"notification_id": str(notify.id), "type": notify.type, "avatar_url": avatar_url, "username": username, "user_id": user_id, "content": post.id, "message": f"{username} Liked your Post {post.title}" if type=='like' else f"{username} Disliked your Post {post.title}"})