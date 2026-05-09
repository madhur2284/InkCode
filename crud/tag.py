from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.db_models import Tag
from fastapi import HTTPException, status

async def get_tag_by_name(name: str, db: AsyncSession) -> Tag:
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    return tag


async def add_tag(name: str, slug: str, description: str, db: AsyncSession) -> Tag:
    tag = Tag(name=name, slug=slug, description=description)
    db.add(tag)
    try:
        await db.commit()
        await db.refresh(tag)
        return tag
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")


async def get_tag_by_slug(slug: str, db: AsyncSession) -> Tag:
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    tag = result.scalar_one_or_none()

    return tag

async def delete_tag_by_slug(slug: str, db: AsyncSession):
    tag = await get_tag_by_slug(slug, db)
    if not tag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No tag exist with this slug")
    
    try:
        await db.delete(tag)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error:{e}")