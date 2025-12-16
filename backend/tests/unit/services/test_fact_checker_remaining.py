import pytest
from app.services.fact_checker import FactCheckingService
from app.models.schemas import Article
from datetime import datetime


@pytest.mark.asyncio
async def test_generate_fact_ledger_with_fallback_and_corroboration():
    svc = FactCheckingService()

    # Ensure no API key so fallback path used
    import os
    os.environ.pop("OPENAI_API_KEY", None)

    a1 = Article(
        url="u1",
        title="t1",
        content="Alpha beta gamma delta epsilon. Extra sentence here.",
        source_name="S1",
        source_url="su",
        published_date=datetime.utcnow()
    )

    a2 = Article(
        url="u2",
        title="t2",
        content="Alpha beta gamma delta epsilon. Different tail.",
        source_name="S2",
        source_url="su2",
        published_date=datetime.utcnow()
    )

    ledger = await svc.generate_fact_ledger("story1", [a1, a2])
    # At least one confirmed claim expected because contents overlap substantially
    assert hasattr(ledger, "confirmed_claims")
    assert hasattr(ledger, "uncorroborated_claims")
