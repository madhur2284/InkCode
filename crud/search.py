from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, select, exists
from sqlalchemy.orm import selectinload
from models.db_models import Post, Reaction, Comment, Bookmark
import math

async def get_posts(db: AsyncSession, query: str, limit: int, page: int, user_id: int):
    ts_query = func.websearch_to_tsquery('english', query)

    ts_rank = func.ts_rank_cd(Post.search_vector, ts_query)

    fuzzy_search = func.similarity(Post.title, query)

    result = await db.execute(select(func.count()).where(
        Post.is_active == True,
        Post.status == 'published',
        or_(
        Post.search_vector.op("@@")(ts_query),
        fuzzy_search > 0.3
        )
    ))

    total_rows = result.scalar_one_or_none()

    if not total_rows or (total_rows == 0):
        return {
            "total_pages": 0,
            "current_page": page,
            "limit": limit,
            "has_previous": False,
            "has_next": False,
            "data": []
        }
    
    total_pages = math.ceil(total_rows/limit)

    skip = (page - 1) * limit

    like_count_query = select(func.count()).where(Reaction.post_id == Post.id, Reaction.type == 'like').correlate(Post).scalar_subquery()
    dislike_count_query = select(func.count()).where(Reaction.post_id == Post.id, Reaction.type == 'dislike').correlate(Post).scalar_subquery()
    bookmark_count_query = select(func.count()).where(Bookmark.post_id == Post.id).correlate(Post).scalar_subquery()
    comment_count_query = select(func.count()).where(Comment.post_id == Post.id).correlate(Post).scalar_subquery()
    
    is_liked_query = select(exists().where(Reaction.post_id == Post.id, Reaction.user_id == user_id, Reaction.type == 'like')).scalar_subquery()
    is_disliked_query = select(exists().where(Reaction.post_id == Post.id, Reaction.user_id == user_id, Reaction.type == 'dislike')).scalar_subquery()
    is_bookmarked_query = select(exists().where(Bookmark.post_id == Post.id, Bookmark.user_id == user_id)).scalar_subquery()

    result = await db.execute(select(
        Post,
        like_count_query.label("like_count"),
        dislike_count_query.label("dislike_count"),
        bookmark_count_query.label("bookmark_count"),
        comment_count_query.label("comment_count"),
        is_liked_query.label("is_liked"),
        is_disliked_query.label("is_disliked"),
        is_bookmarked_query.label("is_bookmarked"),
        ts_rank.label("rank")
    ).
    options(selectinload(Post.author)).
    where(
        Post.is_active == True,
        Post.status == "published",
        or_(
            Post.search_vector.op("@@")(ts_query),
            fuzzy_search > 0.3
        )
    ).
    order_by(ts_rank.desc(), fuzzy_search.desc()).offset(skip).limit(limit)
    )

    rows = result.all()

    return {
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "has_previous": False if page==1 else True,
        "has_next": False if page==total_pages else True,
        "data": [
            {
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "author": post.author, 
                "content": post.content[:150],
                "view_count": post.view_count,
                "like_count": like_count,
                "dislike_count": dislike_count,
                "bookmark_count": bookmark_count,
                "comment_count": comment_count,
                "is_liked": is_like,
                "is_disliked": is_dislike,
                "is_bookmarked": is_bookmark,
            }
            for post, like_count, dislike_count, bookmark_count, comment_count, is_like, is_dislike, is_bookmark, rank in rows
        ]
    }
  