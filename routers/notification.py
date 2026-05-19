from fastapi.sse import EventSourceResponse
from fastapi import APIRouter, Depends, status, HTTPException, status, Path
from services.auth import get_current_user
from database import get_db
import json
from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import Notification
from sqlalchemy import select, update
from schemas.notification import NotificationResponse
from uuid import UUID
from services.notification import user_queue
from sqlalchemy.orm import selectinload
from asyncio.queues import Queue

router = APIRouter(prefix="/notification", tags=["notification"])

@router.get(path='/stream', response_class=EventSourceResponse)
async def notification(current_user = Depends(get_current_user)):
    q = Queue()
    user_queue[current_user.id] = q
    try:
        while True:
            message = await user_queue[current_user.id].get()
            yield {
                "data": json.dumps(message)
            }
    finally:
        user_queue.pop(current_user.id)


@router.get(path='/', status_code=status.HTTP_200_OK, response_model=list[NotificationResponse])
async def get_notifications(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).options(selectinload(Notification.actor)).where(Notification.recipient_id == current_user.id, Notification.is_read==False).order_by(Notification.created_at.desc()))
    notifications = result.scalars().all()
    if not notifications:
        return []
    
    return [{
        "notification_id": notification.id,
        "type": notification.type,
        "avatar_url": notification.actor.avatar_url,
        "username": notification.actor.username,
        "user_id": notification.actor.id,
        "post_id": notification.post_id,
        "comment_id": notification.comment_id
    }
    for notification in notifications]


@router.post(path='/read/{notification_id}', status_code=status.HTTP_200_OK)
async def mark_read(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), notification_id: UUID = Path(description="Notification ID")):
    try:
        await db.execute(update(Notification).values(is_read=True).where(Notification.id == notification_id))
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")

    return {"message": "Notification marked as read"}

    
    
    