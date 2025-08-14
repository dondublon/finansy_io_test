from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models # , schemas

async def get_item(db: AsyncSession, key: str):
    result = await db.execute(select(models.Item))
    return result.scalars().all()

async def create_item(db: AsyncSession, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item
