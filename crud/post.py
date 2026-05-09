from fastapi import HTTPException, status
from models.db_models import Post, Comment, Reaction, PostTag, Bookmark
from sqlalchemy.ext.asyncio import AsyncSession
from services.reading_time import reading_time
from sqlalchemy import func, select, and_, update, exists
from sqlalchemy.orm import selectinload
from typing import List
import math

async def add_post(db: AsyncSession, title: str, slug: str, content: str, author_id: int, status: str):
    min = reading_time(content)
    post = Post(title = title, slug = slug, content=content, author_id = author_id, status=status, reading_time=min, published_at=func.now() if status == "published" else None, is_active=True)
    db.add(post)
    try:
        await db.commit()
        await db.refresh(post)
        return post
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = 400, detail=f"Error: {e}")

async def add_tag_in_post(db: AsyncSession, tag_id: int, post_id: int):
    try:
        db.add(PostTag(tag_id=tag_id, post_id=post_id))
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")



async def increase_view_count(db: AsyncSession, post_slug: str):
    try:
        await db.execute(update(Post).where(Post.slug == post_slug, Post.is_active == True).values(view_count = Post.view_count+1))
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")
    

async def get_post_detail(slug: str, db: AsyncSession, current_user_id):
    try:
        await increase_view_count(db, slug)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")
    
    like_count_query = select(func.count()).where(and_(Reaction.type == "like", Reaction.post_id == Post.id)).correlate(Post).scalar_subquery()
    dislike_count_query = select(func.count()).where(and_(Reaction.type == "dislike", Reaction.post_id == Post.id)).correlate(Post).scalar_subquery()
    comments_count_query = select(func.count()).where(and_(Comment.post_id == Post.id, Comment.is_active == True)).correlate(Post).scalar_subquery()
    bookmark_count_query = select(func.count()).where(Bookmark.post_id == Post.id).correlate(Post).scalar_subquery()
    is_liked_query = select(exists().where(Reaction.type == "like", Reaction.post_id == Post.id, Reaction.user_id == current_user_id)).scalar_subquery()
    is_disliked_query = select(exists().where(Reaction.type == "dislike", Reaction.post_id == Post.id, Reaction.user_id == current_user_id)).scalar_subquery()
    is_bookmarked_query = select(exists().where(Bookmark.user_id == current_user_id, Bookmark.post_id == Post.id)).scalar_subquery()
    
    result = await db.execute(select(
        Post,
        like_count_query,
        dislike_count_query,
        comments_count_query,
        bookmark_count_query,
        is_liked_query,
        is_disliked_query,
        is_bookmarked_query
    ).options(selectinload(Post.author), selectinload(Post.tags).selectinload(PostTag.tag)).where(Post.slug == slug, Post.is_active == True, Post.status == "published"))

    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Post didn't exist")

    return {
        "id": row[0].id,
        "title": row[0].title,
        "slug": row[0].slug,
        "content": row[0].content,
        "status": row[0].status,
        "reading_time": row[0].reading_time,
        "author": row[0].author,
        "tags": [pt.tag for pt in row[0].tags],
        "comment_count": row[3],
        "bookmark_count": row[4],
        "like_count": row[1],
        "dislike_count": row[2],
        "view_count": row[0].view_count,
        "is_liked": row[5],
        "is_disliked": row[6],
        "is_bookmarked": row[7],
        "created_at": row[0].created_at,
        "updated_at": row[0].updated_at,
        "published_at": row[0].published_at
    }


async def get_post_for_update(slug: str, author_id: int ,db: AsyncSession):
    result = await db.execute(select(Post).options(selectinload(Post.tags)).where(Post.slug == slug, Post.author_id == author_id,Post.is_active == True))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post didn't Exist")
    return post


async def get_posts_pagination(db: AsyncSession, user_id: int, limit: int, skip: int, total_pages: int, page):
    like_count_query = select(func.count()).where(and_(Reaction.type == "like", Reaction.post_id == Post.id)).correlate(Post).scalar_subquery()
    dislike_count_query = select(func.count()).where(and_(Reaction.type == "dislike", Reaction.post_id == Post.id)).correlate(Post).scalar_subquery()
    comments_count_query = select(func.count()).where(and_(Comment.post_id == Post.id, Comment.is_active == True)).correlate(Post).scalar_subquery()
    bookmark_count_query = select(func.count()).where(Bookmark.post_id == Post.id).correlate(Post).scalar_subquery()
    is_liked_query = select(exists().where(Reaction.type == "like", Reaction.post_id == Post.id, Reaction.user_id == user_id)).scalar_subquery()
    is_disliked_query = select(exists().where(Reaction.type == "dislike", Reaction.post_id == Post.id, Reaction.user_id == user_id)).scalar_subquery()
    is_bookmarked_query = select(exists().where(Bookmark.user_id == user_id, Bookmark.post_id == Post.id)).scalar_subquery()

    result = await db.execute(
        select(
            Post,
            like_count_query,
            dislike_count_query,
            comments_count_query,
            bookmark_count_query,
            is_liked_query,
            is_disliked_query,
            is_bookmarked_query
        ).options(selectinload(Post.author), selectinload(Post.tags).selectinload(PostTag.tag)).where(Post.is_active == True, Post.status == "published").offset(skip).limit(limit)
    )

    rows = result.all()

    if not rows:
        return {
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit,
            "has_previous": page > 1,
            "has_next": page < total_pages,
            "data": []
        }

    return {
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "has_previous": False if page == 1 else True,
        "has_next": False if page == total_pages else True,
        "data": [
            {
                "id": row[0].id,
                "title": row[0].title,
                "slug": row[0].slug,
                "content": row[0].content[:50],
                "status": row[0].status,
                "reading_time": row[0].reading_time,
                "author": row[0].author,
                "tags": [pt.tag for pt in row[0].tags],
                "comment_count": row[3],
                "bookmark_count": row[4],
                "like_count": row[1],
                "dislike_count": row[2],
                "view_count": row[0].view_count,
                "is_liked": row[5],
                "is_disliked": row[6],
                "is_bookmarked": row[7],
                "created_at": row[0].created_at,
                "updated_at": row[0].updated_at,
                "published_at": row[0].published_at
            }
            for row in rows
        ]
    }


async def post_pagination(db: AsyncSession, limit: int, page: int):
    result = await db.execute(select(func.count()).where(Post.is_active == True, Post.status == "published"))
    total_rows = result.scalar_one()
    total_pages = math.ceil(total_rows/limit)
    if page > total_pages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"This page didn't exist")
    
    skip_count = (page-1)*limit

    return{
        "total_pages": total_pages,
        "skip": skip_count
    }