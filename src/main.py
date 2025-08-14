import string
import secrets
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from .database import Base, get_db, init_db
from .models import Link
from .schemas import LinkCreate, LinkCreateResponse
from fastapi import APIRouter

alphabet = string.ascii_letters + string.digits

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine, AsyncSessionLocal = init_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/api/v1")


def get_short_key():
    short_key = ''.join(secrets.choice(alphabet) for _ in range(6))
    return short_key

@router.post("/shorten", response_model=LinkCreateResponse)
async def create_short_link(payload: LinkCreate, db: AsyncSession = Depends(get_db)):
    short_key = get_short_key()
    db_link = Link(short_key=short_key, url=str(payload.url))
    db.add(db_link)
    await db.commit()
    # await db.refresh(db_link)
    return db_link


@router.get("/s/{short_key}")
async def redirect_short_link(short_key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.short_key == short_key))
    link = result.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    link.use_counter += 1
    await db.commit()
    return RedirectResponse(url=link.url)


@router.get("/stats/{key}")
async def get_stats(key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.short_key == key))
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return {
        "original_url": link.url,
        "clicks": link.use_counter,
        "created_at": link.created_at
    }
app.include_router(router)
