from pydantic import BaseModel
from typing import List


class Author(BaseModel):
    id : int
    username : str
    slug : str
    avatar_url : str

class Search(BaseModel):
    id: int
    title: str
    slug: str
    author: Author 
    content: str
    view_count: int
    like_count: int
    dislike_count: int
    bookmark_count: int
    comment_count: int
    is_liked: bool
    is_disliked: bool
    is_bookmarked: bool


class SearchResponse(BaseModel):
    total_pages: int
    current_page: int
    limit: int
    has_previous: bool
    has_next: bool
    data: List[Search]
    model_config = {"from_attributes": True}