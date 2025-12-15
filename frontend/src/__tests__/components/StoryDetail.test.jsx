import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import StoryDetail from '../../components/StoryDetail'
import { storyService, factCheckerService } from '../../services/api'

vi.mock('../../services/api', () => ({
  storyService: {
    getStory: vi.fn(),
    getStoryArticles: vi.fn(),
    getStoryCoverage: vi.fn()
  },
  factCheckerService: {
    getFactLedger: vi.fn(),
    generateFactLedger: vi.fn()
  }
}))

describe('StoryDetail', () => {
  const mockStory = {
    story_id: 'story1',
    title: 'Test Story',
    summary: 'Test summary',
    article_count: 3,
    category: 'politics',
    sources_covered: ['BBC News', 'CNN']
  }

  const mockArticles = [
    {
      source_name: 'BBC News',
      title: 'Article 1',
      published_date: '2024-01-01T12:00:00'
    },
    {
      source_name: 'CNN',
      title: 'Article 2',
      published_date: '2024-01-01T13:00:00'
    }
  ]

  const mockCoverage = {
    coverage: {
      'BBC News': true,
      'CNN': true,
      'Reuters': false,
      'The Guardian': false
    },
    sources_covered: ['BBC News', 'CNN'],
    coverage_percentage: 50
  }

  const mockFactLedger = {
    confirmed_claims: [
      {
        text: 'Confirmed claim',
        attribution: 'BBC News',
        supporting_sources: ['BBC News', 'CNN'],
        corroboration_count: 2
      }
    ],
    disputed_claims: [],
    uncorroborated_claims: []
  }

  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    storyService.getStory.mockResolvedValue(mockStory)
    storyService.getStoryArticles.mockResolvedValue(mockArticles)
    storyService.getStoryCoverage.mockResolvedValue(mockCoverage)
    factCheckerService.getFactLedger.mockRejectedValue(new Error('Not found'))
  })

  it('should render story title', async () => {
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Story')).toBeInTheDocument()
    })
  })

  it('should render back button', async () => {
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText(/Back to Stories/)).toBeInTheDocument()
    })
  })

  it('should call onClose when back button clicked', async () => {
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText(/Back to Stories/)).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText(/Back to Stories/))
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('should display coverage matrix', async () => {
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText(/Coverage by Source/)).toBeInTheDocument()
      expect(screen.getByText(/BBC News ✓/)).toBeInTheDocument()
      expect(screen.getByText(/CNN ✓/)).toBeInTheDocument()
      expect(screen.getByText(/Reuters ✗/)).toBeInTheDocument()
    })
  })

  it('should display articles list', async () => {
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText(/Articles in this Story/)).toBeInTheDocument()
      expect(screen.getByText('Article 1')).toBeInTheDocument()
      expect(screen.getByText('Article 2')).toBeInTheDocument()
    })
  })

  it('should show generate fact ledger button', async () => {
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Generate Fact Ledger')).toBeInTheDocument()
    })
  })

  it('should generate fact ledger on button click', async () => {
    factCheckerService.generateFactLedger.mockResolvedValue(mockFactLedger)
    
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Generate Fact Ledger')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Generate Fact Ledger'))

    await waitFor(() => {
      expect(factCheckerService.generateFactLedger).toHaveBeenCalledWith('story1')
      expect(screen.getByText(/Confirmed Claims/)).toBeInTheDocument()
    })
  })

  it('should display confirmed claims', async () => {
    factCheckerService.getFactLedger.mockResolvedValue(mockFactLedger)
    
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Confirmed claim')).toBeInTheDocument()
      expect(screen.getByText(/BBC News, CNN/)).toBeInTheDocument()
    })
  })

  it('should show loading state', () => {
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    expect(screen.getByText(/Loading story details/)).toBeInTheDocument()
  })

  it('should handle error state', async () => {
    storyService.getStory.mockRejectedValue(new Error('Failed to load'))
    
    render(<StoryDetail storyId="story1" onClose={mockOnClose} />)
    
    await waitFor(() => {
      expect(screen.getByText(/Error/)).toBeInTheDocument()
    })
  })
})
