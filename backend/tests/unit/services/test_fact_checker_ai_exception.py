import pytest
import os
import json
from types import SimpleNamespace
from app.services.fact_checker import FactCheckingService
from app.models.schemas import Article
from datetime import datetime


class DummyClient:
    class chat:
        class completions:
            @staticmethod
            def create(*a, **k):
                raise RuntimeError("ai fail")


@pytest.mark.asyncio
async def test_ai_extraction_fallback_on_exception(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    # Monkeypatch openai.OpenAI constructor to return dummy client that raises
    import app.services.fact_checker as fcmod
    monkeypatch.setattr(fcmod, 'openai', SimpleNamespace(OpenAI=lambda api_key=None: DummyClient()))

    svc = FactCheckingService()
    art = Article(
        url="u",
        title="t",
        content="This is a long sentence with many words to be treated as a claim. Another sentence.",
        source_name="S",
        source_url="su",
        published_date=datetime.utcnow()
    )

    claims = await svc.extract_claims([art])
    # fallback should return list of claims via simple extraction
    assert isinstance(claims, list)
    assert len(claims) > 0
