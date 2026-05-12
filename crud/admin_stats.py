from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import Post, Comment, User, Reaction
from sqlalchemy import select, func, or_
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone


async def get_stats(db: AsyncSession):
    total_user_query = select(func.count()).where(User.role=='user').scalar_subquery()
    total_active_user_query = select(func.count()).where(User.is_active==True, User.role=='user').scalar_subquery()
    total_post_query = select(func.count(Post.id)).scalar_subquery() 
    total_active_post_query = select(func.count()).where(Post.is_active == True, Post.status=="published").scalar_subquery()
    total_inactive_post_query = select(func.count()).where(or_(Post.is_active == False, Post.status != 'published')).scalar_subquery()
    total_comment_query = select(func.count()).where(Comment.is_active == True).scalar_subquery()

    new_user_in_last_day = select(func.count()).where(User.created_at >= (datetime.now(timezone.utc) - timedelta(hours=24))).scalar_subquery()
    new_post_in_last_day = select(func.count()).where(Post.created_at >= (datetime.now(timezone.utc) - timedelta(hours=24))).scalar_subquery()
    
    new_user_in_last_month = select(func.count()).where(User.created_at >= (datetime.now(timezone.utc) - timedelta(days=30))).scalar_subquery()
    new_post_in_last_month = select(func.count()).where(Post.created_at >= (datetime.now(timezone.utc) - timedelta(days=30))).scalar_subquery()

    result = await db.execute(select(
        total_user_query,
        total_active_user_query,
        new_user_in_last_day,
        new_user_in_last_month,

        total_post_query,
        total_active_post_query,
        total_inactive_post_query,
        new_post_in_last_day,
        new_post_in_last_month,

        total_comment_query
    ))


    rows = result.all()
    rows = rows[0]
    return {
        "user": {
            "total_users": rows[0],
            "total_active_user": rows[1],
            "new_user_in_last_one_day": rows[2],
            "new_user_in_last_one_month": rows[3]
        },
        "post": {
            "total_posts": rows[4],
            "total_active_post": rows[5],
            "total_inactive_post": rows[6],
            "new_post_in_last_one_day": rows[7],
            "new_post_in_last_one_month": rows[8]
        },
        "total_comments": rows[9]
    }
