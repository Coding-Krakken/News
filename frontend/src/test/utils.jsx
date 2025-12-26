import { render } from "@testing-library/react";

/**
 * Custom render function for testing
 */
export function renderWithProviders(ui, options = {}) {
  return render(ui, { ...options });
}

/**
 * Mock API responses
 */
export const mockApiResponses = {
  stories: [
    {
      story_id: "story1",
      title: "Test Story 1",
      summary: "This is a test story summary",
      article_count: 3,
      sources_covered: ["BBC News", "CNN"],
      category: "politics",
      geographies: ["United States"],
      ideologies: ["center"],
      first_seen: "2024-01-01T12:00:00",
      last_updated: "2024-01-01T15:00:00",
      article_ids: ["url1", "url2", "url3"],
    },
    {
      story_id: "story2",
      title: "Test Story 2",
      summary: "Another test story",
      article_count: 2,
      sources_covered: ["Reuters"],
      category: "technology",
      geographies: ["International"],
      ideologies: ["center"],
      first_seen: "2024-01-02T12:00:00",
      last_updated: "2024-01-02T15:00:00",
      article_ids: ["url4", "url5"],
    },
  ],
  articles: [
    {
      url: "url1",
      title: "Test Article 1",
      content: "Test content 1",
      source_name: "BBC News",
      published_date: "2024-01-01T12:00:00",
      category: "politics",
      geography: "United States",
      ideology: "center",
    },
  ],
  stats: {
    total_articles: 10,
    total_stories: 5,
    by_source: { "BBC News": 4, CNN: 3, Reuters: 3 },
    by_category: { politics: 5, technology: 3, sports: 2 },
    by_geography: { "United States": 6, "United Kingdom": 4 },
    by_ideology: { center: 7, "center-left": 3 },
    by_time: { "1h ago": 2, "3h ago": 3, "6h ago": 5 },
  },
  facets: {
    sources: ["BBC News", "CNN", "Reuters", "The Guardian"],
    categories: ["politics", "technology", "sports"],
    geographies: ["United States", "United Kingdom", "International"],
    ideologies: ["center", "center-left", "center-right"],
  },
  factLedger: {
    story_id: "story1",
    confirmed_claims: [
      {
        text: "Confirmed claim 1",
        attribution: "BBC News",
        article_url: "url1",
        is_confirmed: true,
        supporting_sources: ["BBC News", "CNN"],
        corroboration_count: 2,
      },
    ],
    disputed_claims: [
      {
        text: "Disputed claim 1",
        attribution: "Source A",
        article_url: "url2",
        is_disputed: true,
        disputing_sources: ["Source B"],
      },
    ],
    uncorroborated_claims: [
      {
        text: "Uncorroborated claim 1",
        attribution: "BBC News",
        article_url: "url3",
        is_confirmed: false,
        is_disputed: false,
      },
    ],
    generated_at: "2024-01-01T16:00:00",
  },
  coverage: {
    story_id: "story1",
    coverage: {
      "BBC News": true,
      CNN: true,
      Reuters: false,
      "The Guardian": false,
    },
    sources_covered: ["BBC News", "CNN"],
    total_sources: 4,
    coverage_percentage: 50,
  },
};

/**
 * Create mock axios instance
 */
export function createMockAxios() {
  return {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  };
}
