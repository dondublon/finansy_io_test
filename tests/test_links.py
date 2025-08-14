import unittest
from fastapi.testclient import TestClient
from src.main import app, get_short_key
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
        self.assertEqual(response.status_code, 400)  # FastAPI валидация

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
        key = get_short_key()
        async with self.AsyncSessionLocal() as session:
            link = Link(short_key=key, url="https://example.com/redirect", use_counter=0)
            session.add(link)
            await session.commit()

        # noinspection PyArgumentList
        response = self.client.get(f"/api/v1/s/{key}", follow_redirects=False)
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "https://example.com/redirect")
        # Let's check the counter
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(select(Link).where(Link.short_key == key))
            updated_link = result.scalar_one()
            self.assertEqual(updated_link.use_counter, 1)

    async def test_stats_endpoint(self):
        key = get_short_key()
        async with self.AsyncSessionLocal() as session:
            link = Link(
                short_key=key,
                url="https://example.com",
                use_counter=5
            )
            session.add(link)
            await session.commit()

        # Call endpoint
        response = self.client.get(f"/api/v1/stats/{key}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["original_url"], "https://example.com")
        self.assertEqual(data["clicks"], 5)
        self.assertIn("created_at", data)

    async def test_redirect_short_link_not_found(self):
        non_existent_key = "NOPE01"

        response = self.client.get(f"/api/v1/s/{non_existent_key}", follow_redirects=False)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["detail"], "Link not found")
