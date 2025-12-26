import pytest
from app.database import init_db, close_db, get_database


@pytest.mark.asyncio
async def test_init_and_close_db(monkeypatch):
    # Patch AsyncIOMotorClient to avoid real DB connection
    class DummyClient:
        def __getitem__(self, name):
            class DummyDB:
                class DummyCollection:
                    async def create_index(self, *a, **kw):
                        return None

                articles = DummyCollection()
                stories = DummyCollection()

            return DummyDB()

        def close(self):
            pass

    monkeypatch.setattr("app.database.AsyncIOMotorClient", lambda url: DummyClient())
    await init_db()
    db = get_database()
    assert db is not None
    await close_db()


def test_get_database_returns_none_when_uninitialized(monkeypatch):
    monkeypatch.setattr("app.database.database", None)
    assert get_database() is None
