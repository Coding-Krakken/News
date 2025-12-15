import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import AnalyticsPage from '../../pages/AnalyticsPage'
import { analyticsService } from '../../services/api'

vi.mock('../../services/api', () => ({
  analyticsService: {
    getStats: vi.fn()
  }
}))

describe('AnalyticsPage', () => {
  const mockStats = {
    total_articles: 100,
    total_stories: 25,
    by_source: {
      'BBC News': 40,
      'CNN': 30,
      'Reuters': 20,
      'The Guardian': 10
    },
    by_category: {
      'politics': 50,
      'technology': 30,
      'sports': 20
    },
    by_geography: {
      'United States': 60,
      'United Kingdom': 40
    },
    by_ideology: {
      'center': 70,
      'center-left': 20,
      'center-right': 10
    },
    by_time: {
      '1h ago': 10,
      '3h ago': 20,
      '6h ago': 30,
      '1d ago': 40
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
    analyticsService.getStats.mockResolvedValue(mockStats)
  })

  it('should render page title', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Coverage Analytics')).toBeInTheDocument()
    })
  })

  it('should display overview statistics', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Overview')).toBeInTheDocument()
      expect(screen.getByText('Total Articles')).toBeInTheDocument()
      expect(screen.getByText('100')).toBeInTheDocument()
      expect(screen.getByText('Total Stories')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
    })
  })

  it('should display source statistics', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('By Source')).toBeInTheDocument()
      expect(screen.getByText('BBC News')).toBeInTheDocument()
      expect(screen.getByText('40')).toBeInTheDocument()
      expect(screen.getByText('CNN')).toBeInTheDocument()
      expect(screen.getByText('30')).toBeInTheDocument()
    })
  })

  it('should display category statistics', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('By Category')).toBeInTheDocument()
      expect(screen.getByText('politics')).toBeInTheDocument()
      expect(screen.getByText('50')).toBeInTheDocument()
      expect(screen.getByText('technology')).toBeInTheDocument()
      expect(screen.getByText('30')).toBeInTheDocument()
    })
  })

  it('should display geography statistics', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('By Geography')).toBeInTheDocument()
      expect(screen.getByText('United States')).toBeInTheDocument()
      expect(screen.getByText('60')).toBeInTheDocument()
    })
  })

  it('should display ideology statistics', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('By Ideology')).toBeInTheDocument()
      expect(screen.getByText('center')).toBeInTheDocument()
      expect(screen.getByText('70')).toBeInTheDocument()
    })
  })

  it('should display time statistics', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('By Time')).toBeInTheDocument()
      expect(screen.getByText('1h ago')).toBeInTheDocument()
      expect(screen.getByText('10')).toBeInTheDocument()
    })
  })

  it('should show loading state', () => {
    render(<AnalyticsPage />)
    expect(screen.getByText(/Loading analytics/)).toBeInTheDocument()
  })

  it('should handle error state', async () => {
    analyticsService.getStats.mockRejectedValue(new Error('Failed to load'))
    
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/Error/)).toBeInTheDocument()
    })
  })

  it('should handle empty categories', async () => {
    const statsWithoutCategories = {
      ...mockStats,
      by_category: {}
    }
    analyticsService.getStats.mockResolvedValue(statsWithoutCategories)
    
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('By Category')).toBeInTheDocument()
      expect(screen.getByText(/No categories available/)).toBeInTheDocument()
    })
  })
})
