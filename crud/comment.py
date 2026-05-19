from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import Comment, CommentReaction, Notification, Post
from sqlalchemy import func, select, exists
from sqlalchemy.orm import selectinload, aliased
from schemas.comment import CommentBasicResponse
from typing import List
from fastapi import HTTPException, status
from services.pagination_calculate import pagination_calculate
from services.notification import initiate_notification
import math

async def add_comment(content: str, user_id: int, post_id: int, parent_id: int | None, db: AsyncSession) -> dict:
    comment = Comment()
    comment.content = content
    comment.author_id = user_id
    comment.post_id = post_id
    comment.parent_id = parent_id
    db.add(comment)
    try:
        await db.commit()
        await db.refresh(comment)
        return {
            "id": comment.id,
            "content": comment.content,
            "post_id": comment.post_id,
            "parent_id": comment.parent_id,
            "author_id": comment.author_id,
            "is_active": comment.is_active,
            "created_at": comment.created_at,
            "edited_at": comment.edited_at
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")


async def get_comments(user_id:int ,db: AsyncSession, post_id:int, limit: int, skip: int, order_by: str) -> List[dict]:
    Reply = aliased(Comment)
    like_count = select(func.count()).where(CommentReaction.comment_id == Comment.id, CommentReaction.type == "like").correlate(Comment).scalar_subquery()
    dislike_count = select(func.count()).where(CommentReaction.comment_id == Comment.id, CommentReaction.type == "dislike").correlate(Comment).scalar_subquery()
    reply_count = select(func.count()).where(Reply.parent_id == Comment.id).correlate(Comment).scalar_subquery()
    is_liked = select(exists().where(CommentReaction.type=="like", CommentReaction.comment_id == Comment.id, CommentReaction.user_id==user_id)).scalar_subquery()
    is_disliked = select(exists().where(CommentReaction.type=="dislike", CommentReaction.comment_id==Comment.id, CommentReaction.user_id==user_id)).scalar_subquery()


    result = await db.execute(
        select(
            Comment,
            like_count.label("like_count"),
            dislike_count.label("dislike_count"),
            reply_count.label("reply_count"),
            is_liked.label("is_liked"),
            is_disliked.label("is_disliked")
        ).options(selectinload(Comment.reactions), selectinload(Comment.replies)).where(Comment.is_active == True, Comment.post_id == post_id, Comment.parent_id == None).order_by(Comment.created_at.desc() if order_by == "desc" else Comment.created_at.asc()).offset(skip).limit(limit)
    )

    rows = result.all()

    return[
        {
            "id": comment.id,
            "content": comment.content,
            "post_id": comment.post_id,
            "author_id": comment.author_id,
            "parent_id": comment.parent_id,
            "like_count": like,
            "dislike_count": dislike,
            "reply_count": reply,
            "is_liked": is_liked,
            "is_disliked": is_disliked,
            "is_active": comment.is_active,
            "created_at": comment.created_at,
            "edited_at": comment.edited_at
        }
        for comment, like, dislike, reply, is_liked, is_disliked in rows
    ]


async def get_comment(db: AsyncSession, comment_id: int, page: int, limit: int, user_id: int):
    result = await db.execute(select(func.count()).where(Comment.parent_id == comment_id, Comment.is_active == True))
    total_rows = result.scalar()
    total_pages = math.ceil(total_rows/limit)
    if total_pages == 0:
        return {
            "total_pages": 0,
            "current_page": page,
            "limit": limit,
            "has_previous": False,
            "has_next": False,
            "data":[]
        }

    skip = (page-1)*limit

    Reply = aliased(Comment)
    like_count = select(func.count()).where(CommentReaction.comment_id == Comment.id, CommentReaction.type == "like").correlate(Comment).scalar_subquery()
    dislike_count = select(func.count()).where(CommentReaction.comment_id == Comment.id, CommentReaction.type=="dislike").correlate(Comment).scalar_subquery()
    reply_count = select(func.count()).where(Reply.parent_id == Comment.id, Comment.is_active == True).correlate(Comment).scalar_subquery()
    is_liked = select(exists().where(CommentReaction.type=="like", CommentReaction.comment_id == Comment.id, CommentReaction.user_id==user_id)).scalar_subquery()
    is_disliked = select(exists().where(CommentReaction.type=="dislike", CommentReaction.comment_id==Comment.id, CommentReaction.user_id==user_id)).scalar_subquery()
    result = await db.execute(select(Comment, like_count, dislike_count, reply_count, is_liked, is_disliked).options(selectinload(Comment.reactions)).where(Comment.parent_id == comment_id).order_by(Comment.created_at.desc()).offset(skip).limit(limit))
    replies = result.all()
    

    return {
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "has_previous": False if page == 1 else True,
        "has_next": False if page == total_pages else True,
        "data":[
            {
                "id": comment.id,
                "content": comment.content,
                "post_id": comment.post_id,
                "author_id": comment.author_id,
                "parent_id": comment.parent_id,
                "like_count": like,
                "dislike_count": dislike,
                "reply_count": reply,
                "is_liked": is_liked,
                "is_disliked": is_disliked,
                "is_active": comment.is_active,
                "created_at": comment.created_at,
                "edited_at": comment.edited_at    
            }for comment, like, dislike, reply, is_liked, is_disliked in replies
        ]
    }


async def update(db: AsyncSession, comment_id: int, author_id: int, content: str):
    try:
        result = await db.execute(select(Comment).where(Comment.id == comment_id, Comment.is_active == True, Comment.author_id == author_id))
        comment = result.scalar_one()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment didn't found")
    
    comment.content = content

    try:
        await db.commit()
        await db.refresh(comment)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't update comment")
    
    return {
        "id": comment.id,
        "content": comment.content,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "parent_id": comment.parent_id,
        "is_active": comment.is_active,
        "created_at": comment.created_at,
        "edited_at":comment.edited_at,
    }
    

async def soft_delete_comment(db: AsyncSession, comment_id: int, author_id: int):
    result = await db.execute(select(Comment).where(Comment.id == comment_id, Comment.is_active == True, Comment.author_id == author_id))
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No comment found")
    
    comment.is_active = False
    try:
        await db.commit()
        await db.refresh(comment)
        return comment
    except:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="coudn't update")
    

async def create_comment_notification(db: AsyncSession, avatar_url: str, username: str, user_id: int, post_id: int, parent_id: int | None, comment_id: int):
    notify = Notification()
    comment = Comment()
    post = Post()
    if parent_id:
        result = await db.execute(select(Comment).options(selectinload(Comment.parent)).where(Comment.id == comment_id))
        comment = result.scalar_one_or_none()
        if user_id == comment.author_id:
            return
        notify.recipient_id = comment.parent.author_id
        notify.type = "comment_reply"
    else:
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if post.author_id == user_id:
            return
        notify.recipient_id = post.author_id
        notify.post_id = post_id
        notify.type = "post_comment"

    notify.actor_id = user_id
    notify.comment_id = comment_id

    
    db.add(notify)
    await db.commit()
    await db.refresh(notify)
    await initiate_notification(notify.recipient_id, {"notification_id": str(notify.id), "type": notify.type, "avatar_url": avatar_url, "username": username, "user_id": user_id, "content": comment_id, "message": f"{username} comment on your post {post.title}" if not parent_id else f"{username} reply on your comment {comment.content}"})
