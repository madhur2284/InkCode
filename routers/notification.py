from fastapi.sse import EventSourceResponse
from asyncio import Queue
from fastapi import APIRouter, Depends, status, HTTPException, status, Path
from services.auth import get_current_user
from database import get_db
import json
from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import Notification
from sqlalchemy import select, update
from schemas.notification import NotificationResponse
from uuid import UUID

router = APIRouter(prefix="/notification", tags=["notification"])

queue = Queue()

@router.get(path='/stream', response_class=EventSourceResponse)
async def notification(current_user = Depends(get_current_user)):
    while True:
        message = await queue.get()
        yield {
            "data": json.dumps(message)
        }


@router.get(path='/', status_code=status.HTTP_200_OK, response_model=list[NotificationResponse])
async def get_notifications(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.recipient_id == current_user.id, Notification.is_read==False).order_by(Notification.created_at.desc()))
    notifications = result.all()
    if not notification:
        return None
    
    return [{
        "notification_id": notification.id,
        "type": notification.type,
        "avatar_url": current_user.avatar_url,
        "username": current_user.username,
        "user_id": current_user.id,
        "post_id": notification.post_id,
        "comment_id": notification.comment_id
    }
    for notification in notifications]


@router.post(path='/read/{notification_id}', status_code=status.HTTP_200_OK)
async def mark_read(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), notification_id: UUID = Path(gt=0, description="Notification ID")):
    try:
        await db.execute(update(Notification).values(is_read=True).where(Notification.id == notification_id))
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")

    result = await db.execute(select(Notification).where(Notification.is_read == False))
    expired_notification = result.all()

    if len(expired_notification) > 0:
        for notification in expired_notification:
            await db.delete(notification)
            await db.commit()

    return {"message": "Notification marked as read"}

    
    
    