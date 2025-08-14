from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def create_async_engine_and_session(database_url: str):
    engine = create_async_engine(database_url, echo=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    return engine, AsyncSessionLocal


DATABASE_URL = "sqlite+aiosqlite:///./main.db"
engine, AsyncSessionLocal = create_async_engine_and_session(DATABASE_URL)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
