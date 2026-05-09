from fastapi import APIRouter, status, Depends, Path, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

from schemas.comment import CommentCreate, CommentBasicResponse, CommentCreateResponse, CommentPaginationResponse
from database import get_db
from models.db_models import Comment
from services.auth import get_current_user
from crud.comment import add_comment, get_comments, get_comment, update, soft_delete_comment
from services.pagination_calculate import pagination_calculate


router = APIRouter(prefix="/comment", tags=["comment"])

@router.post(path='/', status_code=status.HTTP_201_CREATED, response_model=CommentCreateResponse)
async def create_comment(comment: CommentCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await add_comment(comment.content, current_user.id, comment.post_id, comment.parent_id, db)
    return result


@router.get(path="/", status_code=status.HTTP_200_OK, response_model=CommentPaginationResponse)
async def fetch_comments(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db), limit: int = Query(gt=0, default=10, description="number of comments per request"), page: int = Query(ge=1, default=1, description="Page Number"), order_by: Literal["dec", "inc"] = Query(default="inc", description="Order of the result"), post_id: int = Query(gt=0, description="Post id of comments")):
    try:
        pagination_data = await pagination_calculate(db, page, limit, Comment)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")
    
    if pagination_data.get("total_pages") == 0:
        return{
            "total_pages": 0,
            "current_page": 1,
            "limit": limit,
            "has_previous": False,
            "has_next": False,
            "data": []
        }
    
    comments = await get_comments(current_user.id, db, post_id, limit, pagination_data.get("skip"), order_by)
    
    return {
        "total_pages": pagination_data.get("total_pages"),
        "current_page": page,
        "limit": limit,
        "has_previous": False if page == 1 else True,
        "has_next": False if page == pagination_data.get("total_pages") else True,
        "data": comments
    }
    

@router.get(path='/{comment_id}', status_code=status.HTTP_200_OK, response_model=CommentPaginationResponse)
async def fetch_replies(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db), comment_id: int = Path(gt=0, description="comment id"), limit: int = Query(default = 10, gt=0, description="Limit of comments per request"), page: int = Query(default=1, gt=0, description="current page count")):
    try:
        comment = await get_comment(db, comment_id, page, limit, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")
    return comment



@router.patch(path='/{comment_id}', status_code = status.HTTP_200_OK, response_model=CommentCreateResponse)
async def update_comment(content: str = Query(description="content of the updated comments"), db: AsyncSession = Depends(get_db), comment_id: int = Path(gt=0, description="Comment Id"), current_user = Depends(get_current_user)):
    comment = await update(db, comment_id, current_user.id, content)
    return comment


@router.delete(path='/{comment_id}', status_code=status.HTTP_200_OK)
async def soft_delete(db: AsyncSession = Depends(get_db), comment_id: int = Path(gt=0, description="comment id"), current_user = Depends(get_current_user)):
    try:
        comment = await soft_delete_comment(db, comment_id, current_user.id)
        return {"message": f"comment deted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Comment couldn't updated")
    
