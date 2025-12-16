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

// stub Filters to avoid network and provide a way to trigger onFilterChange
vi.mock('../components/Filters', () => ({
  default: ({ onFilterChange }) => {
    const React = require('react')
    return React.createElement('button', { onClick: () => onFilterChange({ sources: ['A'] }) }, 'Trigger Filter')
  }
}))

describe('StoriesPage additional behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // default stories list empty
    storyService.getStories.mockResolvedValue([])
    // noop alert
    vi.stubGlobal('alert', () => {})
  })

  it('shows error when ingest fails', async () => {
    articleService.ingestArticles.mockRejectedValue(new Error('ingest fail'))

    render(<StoriesPage />)

    fireEvent.click(await screen.findByText(/Ingest Articles/))

    await waitFor(() => {
      expect(screen.getByText(/Error: ingest fail/)).toBeInTheDocument()
    })
  })

  it('shows error when cluster fails', async () => {
    storyService.clusterStories.mockRejectedValue(new Error('cluster fail'))

    render(<StoriesPage />)

    fireEvent.click(await screen.findByText(/Cluster Stories/))

    await waitFor(() => {
      expect(screen.getByText(/Error: cluster fail/)).toBeInTheDocument()
    })
  })

  it('calls onFilterChange and logs the filters', async () => {
    const spy = vi.spyOn(console, 'log')

    render(<StoriesPage />)

    fireEvent.click(await screen.findByText('Trigger Filter'))

    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('Filters changed:', { sources: ['A'] })
    })
  })
})
