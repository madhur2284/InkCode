from pydantic import BaseModel
from uuid import UUID

class NotificationResponse(BaseModel):
    notification_id: UUID
    type: str
    avatar_url: str
    username: str
    user_id: int
    post_id: int | None
    comment_id: int | None
    model_config = {"from_attributes": True}