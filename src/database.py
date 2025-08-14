from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

Base = declarative_base()

_engine = None
_AsyncSessionLocal = None

def init_db(database_url: str = None):
    global _engine, _AsyncSessionLocal
    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./main.db")
    _engine, _AsyncSessionLocal = create_async_engine_and_session(database_url)
    return _engine, _AsyncSessionLocal

def create_async_engine_and_session(database_url: str):
    engine = create_async_engine(database_url, echo=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    return engine, AsyncSessionLocal

async def get_db():
    if _AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    async with _AsyncSessionLocal() as session:
        yield session


