from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_lifespan_calls_init_and_close(monkeypatch):
    import app.main as main_module

    called = {"init": False, "close": False}

    async def fake_init():
        called["init"] = True

    async def fake_close():
        called["close"] = True

    monkeypatch.setattr(main_module, "init_db", AsyncMock(side_effect=fake_init))
    monkeypatch.setattr(main_module, "close_db", AsyncMock(side_effect=fake_close))

    # Use the lifespan context manager
    async with main_module.lifespan(main_module.app):
        assert called["init"] is True

    # After exit, close should have been called
    assert called["close"] is True
