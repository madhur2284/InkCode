from pydantic import BaseModel
from typing import Literal

class CommentReactionCreate(BaseModel):
    comment_id: int
    type: Literal["like", "dislike"]