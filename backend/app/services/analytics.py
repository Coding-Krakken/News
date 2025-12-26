from typing import Dict, List
from datetime import datetime
from collections import defaultdict
from ..models.schemas import Article, Story, CoverageStats


class AnalyticsService:
    """Service for computing coverage statistics"""

    def compute_coverage_stats(
        self, articles: List[Article], stories: List[Story]
    ) -> CoverageStats:
        """Compute comprehensive coverage statistics"""

        stats = CoverageStats(total_articles=len(articles), total_stories=len(stories))

        # By source
        by_source = defaultdict(int)
        for article in articles:
            by_source[article.source_name] += 1
        stats.by_source = dict(by_source)

        # By category
        by_category = defaultdict(int)
        for article in articles:
            if article.category:
                by_category[article.category] += 1
        stats.by_category = dict(by_category)

        # By geography
        by_geography = defaultdict(int)
        for article in articles:
            if article.geography:
                by_geography[article.geography] += 1
        stats.by_geography = dict(by_geography)

        # By ideology
        by_ideology = defaultdict(int)
        for article in articles:
            if article.ideology:
                by_ideology[article.ideology] += 1
        stats.by_ideology = dict(by_ideology)

        # By time (hourly buckets for last 24 hours)
        by_time = self._compute_time_stats(articles)
        stats.by_time = by_time

        return stats

    def _compute_time_stats(self, articles: List[Article]) -> Dict[str, int]:
        """Compute article counts by time buckets"""
        now = datetime.utcnow()
        by_time = defaultdict(int)

        for article in articles:
            # Calculate hours ago
            hours_ago = int((now - article.published_date).total_seconds() / 3600)

            if hours_ago < 24:
                bucket = f"{hours_ago}h ago"
                by_time[bucket] += 1
            elif hours_ago < 168:  # Last week
                days_ago = hours_ago // 24
                bucket = f"{days_ago}d ago"
                by_time[bucket] += 1
            else:
                bucket = "older"
                by_time[bucket] += 1

        return dict(by_time)

    def get_story_coverage_matrix(
        self, story: Story, all_sources: List[str]
    ) -> Dict[str, bool]:
        """Get coverage matrix showing which sources covered a story"""
        coverage = {}

        for source in all_sources:
            coverage[source] = source in story.sources_covered

        return coverage

    def filter_articles(
        self,
        articles: List[Article],
        sources: List[str] = None,
        categories: List[str] = None,
        geographies: List[str] = None,
        ideologies: List[str] = None,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> List[Article]:
        """Filter articles based on multiple criteria"""
        filtered = articles

        if sources:
            filtered = [a for a in filtered if a.source_name in sources]

        if categories:
            filtered = [a for a in filtered if a.category in categories]

        if geographies:
            filtered = [a for a in filtered if a.geography in geographies]

        if ideologies:
            filtered = [a for a in filtered if a.ideology in ideologies]

        if start_date:
            filtered = [a for a in filtered if a.published_date >= start_date]

        if end_date:
            filtered = [a for a in filtered if a.published_date <= end_date]

        return filtered
