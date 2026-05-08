from pydantic import BaseModel, Field
from typing import Literal

class PostReactionCreate(BaseModel):
    post_id: int = Field(gt=0, description="post ID")
    type: Literal["like", "dislike"] = Field(description="Type of Reaction Either 'like' or 'dislike'")


 