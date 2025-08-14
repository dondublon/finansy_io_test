# main.py
import secrets
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from .database import engine, Base, get_db
from .models import Link
from .schemas import LinkCreate, LinkCreateResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/shorten", response_model=LinkCreateResponse)
async def create_short_link(payload: LinkCreate, db: AsyncSession = Depends(get_db)):
    short_key = secrets.token_urlsafe(4)[:6]  # 6 символов
    db_link = Link(short_key=short_key, url=str(payload.url))
    db.add(db_link)
    await db.commit()
    await db.refresh(db_link)
    return db_link


@app.get("/{short_key}")
async def redirect_short_link(short_key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.short_key == short_key))
    link = result.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    link.use_counter += 1
    await db.commit()
    return RedirectResponse(url=link.url)
