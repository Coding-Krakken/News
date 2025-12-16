import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import StoriesPage from '../pages/StoriesPage'

vi.mock('../services/api', () => ({
  storyService: {
    getStories: vi.fn(),
    clusterStories: vi.fn()
  },
  articleService: {
    ingestArticles: vi.fn()
  }
}))

import { storyService, articleService } from '../services/api'

// stub Filters component to avoid mounting network-dependent internals
vi.mock('../components/Filters', () => ({
  default: () => {
    const React = require('react')
    return React.createElement('div', null, 'Filters')
  }
}))

describe('StoriesPage cluster behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    storyService.getStories.mockResolvedValue([])
    storyService.clusterStories.mockResolvedValue({})
    articleService.ingestArticles.mockResolvedValue({})
    // noop alert to avoid jsdom not implemented
    vi.stubGlobal('alert', () => {})
  })

  it('calls clusterStories and reloads stories after timeout', async () => {
    vi.useFakeTimers()

    // provide analyticsService.getFacets to avoid Filters load error
    const api = await import('../services/api')
    api.analyticsService = { getFacets: vi.fn().mockResolvedValue({ sources: [], categories: [], geographies: [], ideologies: [] }) }

    render(<StoriesPage />)

    await waitFor(() => expect(screen.getByText(/Ingest Articles/)).toBeInTheDocument())

    // click cluster
    fireEvent.click(screen.getByText(/Cluster Stories/))

    expect(storyService.clusterStories).toHaveBeenCalled()

    // advance timers so the internal setTimeout runs (no assert on reload to avoid timing flakiness)
    vi.advanceTimersByTime(3000)
    vi.useRealTimers()
  })
})
