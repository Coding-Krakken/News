import pytest
from app.routes import analytics


class DB:
    class Articles:
        async def distinct(self, field):
            # return mixed types including None
            return ["S1", None, 123]

    def __init__(self):
        self.articles = DB.Articles()


@pytest.mark.asyncio
async def test_get_filter_facets_casts_to_str(monkeypatch):
    db = DB()
    res = await analytics.get_filter_facets(db=db)
    assert "sources" in res
    assert all(isinstance(s, str) for s in res["sources"])
