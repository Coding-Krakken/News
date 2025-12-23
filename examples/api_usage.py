"""
Example script demonstrating how to use the News Analytics Platform API.
"""

import requests
import time

BASE_URL = "http://localhost:8000/api"

class NewsAnalyticsClient:
    """Client for interacting with the News Analytics Platform API"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def ingest_articles(self):
        """Ingest articles from all configured sources"""
        response = requests.post(f"{self.base_url}/articles/ingest")
        return response.json()
    
    def cluster_stories(self):
        """Trigger story clustering"""
        response = requests.post(f"{self.base_url}/stories/cluster")
        return response.json()
    
    def get_stories(self):
        """Get all stories"""
        response = requests.get(f"{self.base_url}/stories/")
        return response.json()
    
    def get_stats(self):
        """Get coverage statistics"""
        response = requests.get(f"{self.base_url}/analytics/stats")
        return response.json()
    
    def generate_fact_ledger(self, story_id):
        """Generate fact ledger for a story"""
        response = requests.post(f"{self.base_url}/fact-checker/{story_id}")
        return response.json()


if __name__ == "__main__":
    client = NewsAnalyticsClient()
    
    print("1. Ingesting articles...")
    result = client.ingest_articles()
    print(f"   Ingested {result['total_ingested']} articles")
    
    print("\n2. Clustering stories...")
    client.cluster_stories()
    time.sleep(5)
    
    print("\n3. Getting stories...")
    stories = client.get_stories()
    print(f"   Found {len(stories)} stories")
    
    if stories:
        print(f"\n4. Generating fact ledger for first story...")
        try:
            ledger = client.generate_fact_ledger(stories[0]['story_id'])
            print(f"   Confirmed: {len(ledger['confirmed_claims'])}")
        except:
            print("   Requires OpenAI API key")
