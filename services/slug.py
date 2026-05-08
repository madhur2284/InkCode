import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

def create_slug(text: str):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s\_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)

    return text

async def create_unique_slug(text: str, db: AsyncSession, model):
    base_slug = create_slug(text)
    slug = base_slug
    counter = 1
    while True:
        user = await db.execute(select(model).where(model.slug == slug))
        user = user.scalar_one_or_none()
        if not user:
            return slug
        
        slug = f"{base_slug}-{counter}"
        counter += 1
