import pytest
from app.services.fact_checker import FactCheckingService
from app.models.schemas import Article
from app.models.schemas import Claim


class DummyClient:
    class chat:
        class completions:
            @staticmethod
            def create(*args, **kwargs):
                raise RuntimeError("AI service failure")


@pytest.mark.asyncio
async def test_ai_extraction_exception_uses_fallback(monkeypatch):
    # Ensure service thinks it has an API key so AI codepath runs
    class Settings:
        openai_api_key = "fake-key"

    monkeypatch.setattr("app.services.fact_checker.get_settings", lambda: Settings())
    # Patch openai.OpenAI to return a client whose call raises
    monkeypatch.setattr(
        "app.services.fact_checker.openai",
        type("m", (), {"OpenAI": lambda api_key: DummyClient()}),
    )

    svc = FactCheckingService()

    article = Article(
        url="https://example.com",
        title="T",
        content=("This is a long sentence that should be considered a claim. " * 3),
        source_name="Example",
        source_url="https://example.com",
        published_date=__import__("datetime").datetime.utcnow(),
    )

    claims = await svc._extract_claims_from_article(article)
    assert isinstance(claims, list)
    assert len(claims) > 0
    # Confirm items are Claim-like (have text and attribution)
    assert all(hasattr(c, "text") and hasattr(c, "attribution") for c in claims)


@pytest.mark.asyncio
async def test_no_api_key_uses_simple_extraction(monkeypatch):
    class Settings:
        openai_api_key = None

    monkeypatch.setattr("app.services.fact_checker.get_settings", lambda: Settings())

    svc = FactCheckingService()

    article = Article(
        url="https://example.com/noai",
        title="No AI",
        content=("Fallback sentence that is long enough to be a claim. " * 3),
        source_name="Example",
        source_url="https://example.com",
        published_date=__import__("datetime").datetime.utcnow(),
    )

    claims = await svc._extract_claims_from_article(article)
    assert isinstance(claims, list)
    assert len(claims) > 0


def test_group_similar_claims_skips_used_index():
    svc = FactCheckingService()

    # Create three similar claims where index 2 will be marked used by index 0,
    # and then be skipped when considered from index 1's inner loop.
    c0 = Claim(
        text="The mayor visited the school today and praised the students.",
        attribution="A",
        article_url="u",
    )
    c1 = Claim(
        text="Local officials attended a school event and spoke to parents.",
        attribution="B",
        article_url="u",
    )
    c2 = Claim(
        text="The mayor visited the school today and praised the students for their efforts.",
        attribution="C",
        article_url="u",
    )

    groups = svc._group_similar_claims([c0, c1, c2])
    # Ensure grouping returns at least one group and no errors; also that used index skipping occurred
    assert isinstance(groups, list)
    assert sum(len(g) for g in groups) == 3
