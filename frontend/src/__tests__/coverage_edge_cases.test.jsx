import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'

// Single mock providing all service exports used in these tests
vi.mock('../services/api', () => ({
  analyticsService: {
    getFacets: vi.fn(),
    getStats: vi.fn()
  },
  storyService: {
    getStories: vi.fn(),
    clusterStories: vi.fn(),
    getStory: vi.fn(),
    getStoryArticles: vi.fn(),
    getStoryCoverage: vi.fn()
  },
  articleService: {
    ingestArticles: vi.fn()
  },
  factCheckerService: {
    getFactLedger: vi.fn(),
    generateFactLedger: vi.fn()
  }
}))

import Filters from '../components/Filters'
import StoryDetail from '../components/StoryDetail'
import AnalyticsPage from '../pages/AnalyticsPage'
import { analyticsService, storyService, factCheckerService } from '../services/api'

describe('Filters error handling', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('logs error when getFacets rejects', async () => {
    const spy = vi.spyOn(console, 'error')
    analyticsService.getFacets.mockRejectedValue(new Error('no network'))

    render(<Filters onFilterChange={() => {}} />)

    await waitFor(() => {
      expect(spy).toHaveBeenCalled()
    })
  })
})

describe('StoryDetail generate error', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    storyService.getStory.mockResolvedValue({ story_id: 's', title: 't', summary: '', article_count: 0 })
    storyService.getStoryArticles.mockResolvedValue([])
    storyService.getStoryCoverage.mockResolvedValue(null)
  })

  it('shows error when generateFactLedger fails', async () => {
    factCheckerService.getFactLedger.mockRejectedValue(new Error('not found'))
    factCheckerService.generateFactLedger.mockRejectedValue(new Error('generation failed'))

    render(<StoryDetail storyId="s" onClose={() => {}} />)

    // wait for initial load
    await waitFor(() => expect(screen.queryByText(/Loading story details/)).not.toBeInTheDocument())

    // click generate
    const btn = screen.getByText('Generate Fact Ledger')
    fireEvent.click(btn)

    await waitFor(() => {
      expect(screen.getByText(/Error: generation failed/)).toBeInTheDocument()
    })
  })
})

describe('AnalyticsPage empty stats', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows empty state when stats is falsy', async () => {
    analyticsService.getStats.mockResolvedValue(null)

    render(<AnalyticsPage />)

    await waitFor(() => {
      expect(screen.getByText(/No data available/)).toBeInTheDocument()
    })
  })
})
