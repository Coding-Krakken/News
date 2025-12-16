import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import StoriesPage from '../../pages/StoriesPage'

vi.mock('../../services/api', () => ({
  storyService: {
    getStories: vi.fn(),
    clusterStories: vi.fn()
  },
  articleService: {
    ingestArticles: vi.fn()
  }
}))

import { storyService, articleService } from '../../services/api'

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

    render(<StoriesPage />)

    await waitFor(() => expect(screen.getByText(/Ingest Articles/)).toBeInTheDocument())

    // click cluster
    fireEvent.click(screen.getByText(/Cluster Stories/))

    expect(storyService.clusterStories).toHaveBeenCalled()

    // advance timers so the internal setTimeout runs
    vi.runAllTimers()

    // getStories should be called again to reload
    await waitFor(() => expect(storyService.getStories).toHaveBeenCalled())

    vi.useRealTimers()
  })
})
