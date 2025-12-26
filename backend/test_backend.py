"""
Simple test script to verify the backend is working correctly.
Run with: python test_backend.py
"""

import requests
import time

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed")


def test_ingest_articles():
    """Test article ingestion"""
    print("\nTesting article ingestion...")
    response = requests.post(f"{BASE_URL}/api/articles/ingest")
    assert response.status_code == 200
    data = response.json()
    print(
        f"✓ Ingested {data.get('total_ingested', 0)} articles from {data.get('total_sources', 0)} sources"
    )
    return data


def test_get_sources():
    """Test getting sources"""
    print("\nTesting get sources...")
    response = requests.get(f"{BASE_URL}/api/articles/sources/list")
    assert response.status_code == 200
    sources = response.json()
    print(f"✓ Found {len(sources)} configured sources")
    for source in sources:
        print(f"  - {source['name']} ({source['ideology']})")
    return sources


def test_cluster_stories():
    """Test story clustering"""
    print("\nTesting story clustering...")
    response = requests.post(f"{BASE_URL}/api/stories/cluster")
    assert response.status_code == 200
    print("✓ Clustering started in background")
    print("  Waiting 5 seconds for clustering to complete...")
    time.sleep(5)


def test_get_stories():
    """Test getting stories"""
    print("\nTesting get stories...")
    response = requests.get(f"{BASE_URL}/api/stories/")
    assert response.status_code == 200
    stories = response.json()
    print(f"✓ Found {len(stories)} stories")
    if stories:
        print(f"  First story: {stories[0].get('title', 'N/A')}")
    return stories


def test_analytics():
    """Test analytics endpoint"""
    print("\nTesting analytics...")
    response = requests.get(f"{BASE_URL}/api/analytics/stats")
    assert response.status_code == 200
    stats = response.json()
    print("✓ Analytics retrieved")
    print(f"  Total articles: {stats.get('total_articles', 0)}")
    print(f"  Total stories: {stats.get('total_stories', 0)}")
    return stats


def test_facets():
    """Test facets endpoint"""
    print("\nTesting facets...")
    response = requests.get(f"{BASE_URL}/api/analytics/facets")
    assert response.status_code == 200
    facets = response.json()
    print("✓ Facets retrieved")
    print(f"  Sources: {len(facets.get('sources', []))}")
    print(f"  Categories: {len(facets.get('categories', []))}")
    print(f"  Geographies: {len(facets.get('geographies', []))}")
    print(f"  Ideologies: {len(facets.get('ideologies', []))}")
    return facets


def main():
    print("=================================")
    print("News Analytics Platform - Backend Test")
    print("=================================")

    try:
        # Test basic health
        test_health()

        # Test sources
        sources = test_get_sources()

        # Test ingestion
        ingest_result = test_ingest_articles()

        # Test clustering
        test_cluster_stories()

        # Test stories
        stories = test_get_stories()

        # Test analytics
        stats = test_analytics()

        # Test facets
        facets = test_facets()

        print("\n=================================")
        print("✓ All tests passed!")
        print("=================================")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend")
        print("Make sure the backend is running on http://localhost:8000")
        print("Start it with: cd backend && uvicorn app.main:app --reload")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
