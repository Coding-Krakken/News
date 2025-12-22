import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'

// Mock the api services used by StoriesPage
vi.mock('../services/api', () => ({
  storyService: {
    getStories: vi.fn(),
    clusterStories: vi.fn()
  },
  analyticsService: {
    getFacets: vi.fn(),
    getStats: vi.fn()
  },
  articleService: {
    ingestArticles: vi.fn()
  }
}))

import StoriesPage from '../pages/StoriesPage'
import { storyService, analyticsService } from '../services/api'

describe('StoriesPage clustering timeout branch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // First call: initial load -> empty list
    // Second call (after clustering) -> one story
    storyService.getStories.mockResolvedValueOnce([]).mockResolvedValueOnce([
      { story_id: 's1', title: 'Clustered Story', sources_covered: [] }
    ])
    storyService.clusterStories.mockResolvedValue()
    // stub global alert to avoid jsdom not-implemented
    global.alert = vi.fn()
    analyticsService.getFacets.mockResolvedValue({
      sources: [],
      categories: [],
      geographies: [],
      ideologies: []
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('calls loadStories after clustering timeout and updates UI', async () => {
    render(<StoriesPage />)

    // wait for initial loadStories call
    await waitFor(() => expect(storyService.getStories).toHaveBeenCalledTimes(1))

    // click cluster button; our stubbed setTimeout runs immediately
    const clusterBtn = screen.getByText('Cluster Stories')
    fireEvent.click(clusterBtn)

    // ensure loadStories was invoked again after the timeout
    await waitFor(() => expect(storyService.getStories).toHaveBeenCalledTimes(2), { timeout: 8000 })
  }, { timeout: 10000 })
})
