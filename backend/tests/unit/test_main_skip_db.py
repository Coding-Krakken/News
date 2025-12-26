import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_lifespan_skips_db_when_env_set(monkeypatch):
    # Ensure SKIP_DB_CHECK triggers the branch that skips DB initialization
    monkeypatch.setenv("SKIP_DB_CHECK", "1")

    # Import the module and mock init/close functions that the lifespan would call
    import importlib
    import app.main as mainmod

    importlib.reload(mainmod)

    mainmod.init_db = AsyncMock()
    mainmod.close_db = AsyncMock()

    # Run the lifespan context; it should NOT call init_db when SKIP_DB_CHECK is set
    async with mainmod.lifespan(mainmod.app):
        pass

    assert not mainmod.init_db.called

    # Cleanup
    monkeypatch.delenv("SKIP_DB_CHECK", raising=False)
