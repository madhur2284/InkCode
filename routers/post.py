from fastapi import APIRouter, status, Depends, HTTPException, Path, Query
from schemas.post import PostDetailResponse, PostCreate, PostCreateResponse, PostUpdate, PostsPagination
from schemas.tag import TagResposne
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import User, Post
from services.auth import get_current_user
from services.slug import create_unique_slug
from crud.tag import get_tag_by_slug
from typing import List
from crud.post import add_post, add_tag_in_post, get_post_detail, get_post_for_update, get_posts_pagination
from services.reading_time import reading_time
from services.pagination_calculate import pagination_calculate


router = APIRouter(prefix="/post", tags=["post"])


@router.post(path="/create", status_code=status.HTTP_201_CREATED, response_model=PostDetailResponse)
async def create_post(post: PostCreate , db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        slug = await create_unique_slug(post.title, db, Post)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create slug")
    
    result = await add_post(db, post.title, slug, post.content, current_user.id, post.status)
    
    Tag: TagResposne
    for tag in post.tags:
        Tag = await get_tag_by_slug(tag, db)
        if Tag:
            await add_tag_in_post(db, Tag.id, result.id)

    result = await get_post_detail(slug, db, current_user.id)
    return result


@router.get(path='/posts', status_code=status.HTTP_200_OK, response_model=PostsPagination)
async def get_posts(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), limit: int = Query(default=10, description="Number of Posts per page", gt=0), page: int = Query(default=1, description="Page Number", gt=0)):
    pagination = await pagination_calculate(db, page, limit, Post)
    if pagination.get("total_pages") == 0:
        return {
            "total_pages": 0,
            "current_page": page,
            "limit": limit,
            "has_previous": False,
            "has_next": False,
            "data": []
        }
    
    posts = await get_posts_pagination(db, current_user.id, limit, pagination.get("skip"), pagination.get("total_pages"), page)

    return posts


@router.get(path='/{slug}', status_code=status.HTTP_200_OK, response_model=PostDetailResponse)
async def get_post(slug: str = Path(description="slug of the post"), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    post = await get_post_detail(slug, db, current_user.id)
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Post didn't exist")
    return post


@router.patch(path='/{slug}', status_code=status.HTTP_200_OK, response_model=PostCreateResponse)
async def update_post(Update_post: PostUpdate, current_user = Depends(get_current_user), slug: str = Path(description="slug of the post"), db: AsyncSession = Depends(get_db)):
    post = await get_post_for_update(slug, current_user.id, db)
    update_post_dict = Update_post.model_dump(exclude_none = True)
    
    if update_post_dict.get("title"):
        new_slug = await create_unique_slug(update_post_dict.get("title"), db, Post)
        update_post_dict["slug"] = new_slug

    if update_post_dict.get("content"):
        read_time = reading_time(update_post_dict.get("content"))
        update_post_dict["reading_time"] = read_time
    
    for key, value in update_post_dict.items():
        setattr(post, key, value)

    try:
        await db.commit()
        await db.refresh(post)
        return post
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")


@router.delete(path='/{slug}', status_code=status.HTTP_200_OK)
async def delete_post(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user), slug: str = Path(description="slug of the post")):
    post = await get_post_for_update(slug, current_user.id, db)

    post.is_active = False
    try:
        await db.commit()
        return {"message": "Post Deleted Successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")
    


    

