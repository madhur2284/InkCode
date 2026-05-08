from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal, List
from datetime import datetime


class PostCreate(BaseModel):
    title: str = Field(description="Title of the Post")
    content: str = Field(description="Content of the Post", default="")
    status: Literal["draft", "published", "archived"] = Field(description="status of the post", default="draft")
    tags: List[str] = Field(description="tags used in post")


class PostAuthor(BaseModel):
    username: str
    slug: str
    email: EmailStr
    avatar_url: str


class PostTag(BaseModel):
    id: int
    name: str
    slug: str

class PostCreateResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = Field(default=None)
    status: Literal["draft", "published", "archived"]
    reading_time: int
    author: PostAuthor
    tags: List[PostTag]
    created_at: datetime
    updated_at: datetime
    published_at: datetime



class PostDetailResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: Optional[str] = Field(default=None)
    status: Literal["draft", "published", "archived"]
    reading_time: int
    author: PostAuthor
    tags: List[PostTag]
    comment_count: int
    bookmark_count: int
    like_count: int
    dislike_count: int
    view_count: int
    is_liked: bool
    is_disliked: bool
    is_bookmarked: bool
    created_at: datetime
    updated_at: datetime
    published_at: datetime


# class PostResponse(BaseModel):
#     id: int
#     title: str
#     slug: str
#     status: Literal["draft", "published", "archived"]
#     reading_time: int
#     author: PostAuthor
#     tags: List[PostTag]
#     comment_count: int
#     bookmark_count: int
#     like_count: int
#     dislike_count: int
#     view_count: int
#     is_liked: bool
#     is_bookmarked: bool
#     created_at: datetime
#     updated_at: datetime
#     published_at: datetime


class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    status: Optional[Literal["draft", "published", "archived"]] = Field(default="draft")


class PostsPagination(BaseModel):
    total_pages: int
    current_page: int
    limit: int
    has_previous: bool
    has_next: bool
    data: List[PostDetailResponse]
