"""
Unit tests for analytics route exception branches.
"""

import pytest
from fastapi import HTTPException


def test_get_coverage_stats_handles_db_error(monkeypatch):
    import app.routes.analytics as analytics_module

    class BrokenCursor:
        async def to_list(self, length=None):
            raise Exception("find error")

    class FakeDB:
        def __init__(self):
            self.articles = self
            self.stories = self

        def find(self, *args, **kwargs):
            return BrokenCursor()

    # Call the route function directly and expect HTTPException
    with pytest.raises(HTTPException) as excinfo:
        import asyncio

        asyncio.get_event_loop().run_until_complete(
            analytics_module.get_coverage_stats(db=FakeDB())
        )

    assert excinfo.value.status_code == 500
