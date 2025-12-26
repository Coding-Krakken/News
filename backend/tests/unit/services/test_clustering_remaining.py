import pytest
from app.services.clustering import StoryClusteringService
from app.models.schemas import Article


def make_article(embedding=None):
    return Article(
        url="u",
        title="t",
        content="c",
        source_name="s",
        source_url="su",
        published_date=__import__("datetime").datetime.utcnow(),
        embedding=embedding,
    )


def test_calculate_similarity_without_embeddings():
    svc = StoryClusteringService()
    a1 = make_article(embedding=None)
    a2 = make_article(embedding=None)
    assert svc.calculate_similarity(a1, a2) == 0.0


def test_calculate_similarity_with_embeddings():
    svc = StoryClusteringService()
    vec = [0.1] * 384 if hasattr(svc.model, "encode") else [1.0, 0.0]
    a1 = make_article(embedding=vec)
    a2 = make_article(embedding=vec)
    sim = svc.calculate_similarity(a1, a2)
    assert pytest.approx(sim, rel=1e-3) == 1.0
