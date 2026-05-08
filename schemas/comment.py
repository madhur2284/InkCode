from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CommentCreate(BaseModel):
    content: str
    post_id: int = Field(gt=0)
    parent_id: int | None = Field(gt=0, default=None)


class CommentCreateResponse(BaseModel):
    id: int = Field(gt=0)
    content: str
    post_id: int = Field(gt=0)
    author_id: int = Field(gt=0)
    parent_id: int | None = Field(gt=0, default=None)
    is_active: bool
    created_at: datetime
    edited_at: datetime


class CommentBasicResponse(BaseModel):
    id: int = Field(gt=0)
    content: str
    post_id: int = Field(gt=0)
    author_id: int = Field(gt=0)
    parent_id: int | None = Field(gt=0, default=None)
    like_count: int
    dislike_count: int
    reply_count: int
    is_liked: bool
    is_disliked: bool
    is_active: bool
    created_at: datetime
    edited_at: datetime


class CommentPaginationResponse(BaseModel):
    total_pages: int
    current_page: int
    limit: int
    has_previous: bool
    has_next: bool
    data: List[CommentBasicResponse]