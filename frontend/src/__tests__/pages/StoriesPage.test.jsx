import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import StoriesPage from '../../pages/StoriesPage'
import { storyService, articleService } from '../../services/api'

vi.mock('../../services/api', () => ({
  storyService: {
    getStories: vi.fn(),
    clusterStories: vi.fn()
  },
  articleService: {
    ingestArticles: vi.fn()
  }
}))

vi.mock('../../components/StoryCard', () => ({
  default: ({ story, onClick }) => (
    <div onClick={() => onClick(story.story_id)} data-testid="story-card">
      {story.title}
    </div>
  )
}))

vi.mock('../../components/StoryDetail', () => ({
  default: ({ storyId, onClose }) => (
    <div data-testid="story-detail">
      Story Detail: {storyId}
      <button onClick={onClose}>Close</button>
    </div>
  )
}))

vi.mock('../../components/Filters', () => ({
  default: ({ onFilterChange }) => (
    <div data-testid="filters">Filters</div>
  )
}))

describe('StoriesPage', () => {
  const mockStories = [
    {
      story_id: 'story1',
      title: 'Test Story 1',
      summary: 'Summary 1',
      article_count: 3,
      sources_covered: ['BBC News']
    },
    {
      story_id: 'story2',
      title: 'Test Story 2',
      summary: 'Summary 2',
      article_count: 2,
      sources_covered: ['CNN']
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    storyService.getStories.mockResolvedValue(mockStories)
    storyService.clusterStories.mockResolvedValue({ message: 'Clustering started' })
    articleService.ingestArticles.mockResolvedValue({ total_ingested: 10 })
  })

  it('should render page controls', async () => {
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Ingest Articles')).toBeInTheDocument()
      expect(screen.getByText('Cluster Stories')).toBeInTheDocument()
      expect(screen.getByText('Refresh')).toBeInTheDocument()
    })
  })

  it('should render filters', async () => {
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByTestId('filters')).toBeInTheDocument()
    })
  })

  it('should load and display stories', async () => {
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Story 1')).toBeInTheDocument()
      expect(screen.getByText('Test Story 2')).toBeInTheDocument()
    })
  })

  it('should handle ingest articles click', async () => {
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Ingest Articles')).toBeInTheDocument()
    })

    // Mock window.alert
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})
    
    fireEvent.click(screen.getByText('Ingest Articles'))

    await waitFor(() => {
      expect(articleService.ingestArticles).toHaveBeenCalled()
      expect(alertSpy).toHaveBeenCalledWith(expect.stringContaining('Articles ingested successfully'))
    })

    alertSpy.mockRestore()
  })

  it('should handle cluster stories click', async () => {
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Cluster Stories')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Cluster Stories'))

    await waitFor(() => {
      expect(storyService.clusterStories).toHaveBeenCalled()
    })
  })

  it('should handle refresh click', async () => {
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Refresh')).toBeInTheDocument()
    })

    storyService.getStories.mockClear()
    fireEvent.click(screen.getByText('Refresh'))

    await waitFor(() => {
      expect(storyService.getStories).toHaveBeenCalled()
    })
  })

  it('should show empty state when no stories', async () => {
    storyService.getStories.mockResolvedValue([])
    
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('No stories yet')).toBeInTheDocument()
      expect(screen.getByText(/Ingest articles and cluster them/)).toBeInTheDocument()
    })
  })

  it('should open story detail on card click', async () => {
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Story 1')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Test Story 1'))

    await waitFor(() => {
      expect(screen.getByTestId('story-detail')).toBeInTheDocument()
      expect(screen.getByText(/Story Detail: story1/)).toBeInTheDocument()
    })
  })

  it('should close story detail', async () => {
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Story 1')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Test Story 1'))

    await waitFor(() => {
      expect(screen.getByTestId('story-detail')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Close'))

    await waitFor(() => {
      expect(screen.queryByTestId('story-detail')).not.toBeInTheDocument()
      expect(screen.getByText('Test Story 1')).toBeInTheDocument()
    })
  })

  it('should show loading state', () => {
    render(<StoriesPage />)
    expect(screen.getByText(/Loading stories/)).toBeInTheDocument()
  })

  it('should handle error state', async () => {
    storyService.getStories.mockRejectedValue(new Error('Failed to load'))
    
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/Error/)).toBeInTheDocument()
    })
  })

  it('should disable buttons during operations', async () => {
    render(<StoriesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Ingest Articles')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Ingest Articles'))

    // Button should show "Ingesting..." text while processing
    await waitFor(() => {
      expect(screen.getByText('Ingesting...')).toBeInTheDocument()
    })
  })
})
