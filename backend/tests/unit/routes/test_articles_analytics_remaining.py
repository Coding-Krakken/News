import pytest
import fastapi
from app.routes import articles, analytics


class BadFindDB:
    def articles(self):
        return self

    def stories(self):
        return self

    def find(self, *args, **kwargs):
        raise RuntimeError("db fail")


@pytest.mark.asyncio
async def test_get_articles_handles_db_error():
    db = BadFindDB()
    with pytest.raises(fastapi.HTTPException) as ei:
        await articles.get_articles(db=db)
    assert ei.value.status_code == 500


@pytest.mark.asyncio
async def test_get_coverage_stats_handles_db_error():
    db = BadFindDB()
    with pytest.raises(fastapi.HTTPException) as ei:
        await analytics.get_coverage_stats(db=db)
    assert ei.value.status_code == 500
