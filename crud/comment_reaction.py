from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import CommentReaction, Comment, Notification
from sqlalchemy import select
from fastapi import HTTPException, status
from services.notification import initiate_notification

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add Reaction")
    

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
    

async def comment_reaction_notification(db: AsyncSession, avatar_url: str, username: str, user_id, comment_id, type: str):
    result = await db.execute(select(Comment).where(Comment.id == comment_id, Comment.is_active==True))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="comment Not Found")
    
    if comment.author_id == user_id:
        return
    notify = Notification(type="comment_like" if type=='like' else "comment_dislike", actor_id=user_id, recipient_id= comment.author_id, comment_id=comment_id)

    db.add(notify)
    await db.commit()
    await db.refresh(notify)
    await initiate_notification(notify.recipient_id, {"notification_id": str(notify.id), "type": notify.type, "avatar_url": avatar_url, "username": username, "user_id": user_id, "content": comment_id, "message": f"{username} Liked your Comment {comment.content}" if type=='like' else f"{username} Disliked your comment {comment.content}"})
    
