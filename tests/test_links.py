import unittest
from fastapi.testclient import TestClient
from src.main import app
from src.database import init_db, Base
from src.models import Link
from sqlalchemy import select

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

class AsyncTestLinks(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        # Создаём TestClient на уровне класса синхронно
        cls.client = TestClient(app)
        # Инициализация асинхронной базы через init_db
        cls.engine, cls.AsyncSessionLocal = init_db(TEST_DB_URL)
        # Создаём таблицы
        import asyncio
        asyncio.run(cls._create_tables())

    @classmethod
    async def _create_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    @classmethod
    async def asyncTearDownClass(cls):
        await cls.engine.dispose()

    async def test_create_short_link_invalid_url(self):
        invalid_url = "not_a_url"
        response = self.client.post("/api/v1/shorten", json={"url": invalid_url})
        self.assertEqual(response.status_code, 422)  # FastAPI валидация

    async def test_create_short_link_valid_url(self):
        valid_url = "https://example.com"
        response = self.client.post("/api/v1/shorten", json={"url": valid_url})
        self.assertEqual(response.status_code, 200)
        short_key = response.json()["short_key"]

        async with self.AsyncSessionLocal() as session:
            result = await session.execute(select(Link).where(Link.short_key == short_key))
            link = result.scalars().first()
        self.assertIsNotNone(link)
        self.assertEqual(link.url, valid_url)

    async def test_redirect_short_link(self):
        # Создаём запись напрямую
        async with self.AsyncSessionLocal() as session:
            link = Link(short_key="ABC123", url="https://example.com/redirect", use_counter=0)
            session.add(link)
            await session.commit()

        # noinspection PyArgumentList
        response = self.client.get("/api/v1/s/ABC123", allow_redirects=False)
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "https://example.com/redirect")
