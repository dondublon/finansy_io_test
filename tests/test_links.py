import os
import unittest
from fastapi.testclient import TestClient
from src.main import app
from src.database import Base, create_async_engine_and_session
from src.models import Link
from sqlalchemy.orm import sessionmaker


TEST_DB = "sqlite+aiosqlite:///./test.db"

class TestLinks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаём отдельный движок и сессию для тестов
        cls.engine, cls.AsyncSessionLocal = create_async_engine_and_session(TEST_DB)
        # Синхронная сессия для прямых запросов (для проверки и подготовки данных)
        cls.SyncSession = sessionmaker(bind=cls.engine.sync_engine)
        # Создаём таблицы
        import asyncio
        asyncio.run(cls.create_tables())
        cls.client = TestClient(app)

    @classmethod
    async def create_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    def tearDownClass(cls):
        # Удаляем файл базы
        cls.engine.sync_engine.dispose()
        db_file = TEST_DB.replace("sqlite+aiosqlite:///", "")
        if os.path.exists(db_file):
            os.remove(db_file)


    def test_create_short_link_invalid_url(self):
        response = self.client.post("/api/v1/shorten", json={"url": "bad-url"})
        # Pydantic выдаёт 422, если URL некорректный
        self.assertEqual(response.status_code, 422)

    def test_create_short_link_valid_url(self):
        valid_url = "https://example.com/test"
        response = self.client.post("/api/v1/shorten", json={"url": valid_url})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("short_key", data)
        short_key = data["short_key"]

        db = self.SyncSession()
        link = db.query(Link).filter(Link.short_key == short_key).first()
        db.close()
        self.assertIsNotNone(link)
        self.assertEqual(link.url, valid_url)

    def test_redirect_short_link(self):
        # Добавляем запись напрямую, без HTTP-запроса
        db = self.SyncSession()
        link = Link(short_key="ABC123", url="https://example.com/redirect", use_counter=0)
        db.add(link)
        db.commit()
        db.close()

        # noinspection PyArgumentList
        response = self.client.get("/api/v1/s/ABC123", allow_redirects=False)
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "https://example.com/redirect")


if __name__ == "__main__":
    unittest.main()
