import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Filters from '../../components/Filters'
import { analyticsService } from '../../services/api'

// Mock the API service
vi.mock('../../services/api', () => ({
  analyticsService: {
    getFacets: vi.fn()
  }
}))

describe('Filters', () => {
  const mockFacets = {
    sources: ['BBC News', 'CNN', 'Reuters'],
    categories: ['politics', 'technology', 'sports'],
    geographies: ['United States', 'United Kingdom'],
    ideologies: ['center', 'center-left', 'center-right']
  }

  const mockOnFilterChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    analyticsService.getFacets.mockResolvedValue(mockFacets)
  })

  it('should render filters title', () => {
    render(<Filters onFilterChange={mockOnFilterChange} />)
    expect(screen.getByText('Filters')).toBeInTheDocument()
  })

  it('should load and display facets', async () => {
    render(<Filters onFilterChange={mockOnFilterChange} />)
    
    await waitFor(() => {
      expect(screen.getByText('BBC News')).toBeInTheDocument()
      expect(screen.getByText('CNN')).toBeInTheDocument()
      expect(screen.getByText('politics')).toBeInTheDocument()
      expect(screen.getByText('technology')).toBeInTheDocument()
    })
  })

  it('should display filter sections', async () => {
    render(<Filters onFilterChange={mockOnFilterChange} />)
    
    await waitFor(() => {
      expect(screen.getByText(/Sources/)).toBeInTheDocument()
      expect(screen.getByText(/Categories/)).toBeInTheDocument()
      expect(screen.getByText(/Geography/)).toBeInTheDocument()
      expect(screen.getByText(/Ideology/)).toBeInTheDocument()
    })
  })

  it('should handle checkbox selection', async () => {
    render(<Filters onFilterChange={mockOnFilterChange} />)
    
    await waitFor(() => {
      expect(screen.getByText('BBC News')).toBeInTheDocument()
    })

    const checkbox = screen.getByLabelText('BBC News')
    fireEvent.click(checkbox)

    await waitFor(() => {
      expect(mockOnFilterChange).toHaveBeenCalledWith(
        expect.objectContaining({
          sources: ['BBC News']
        })
      )
    })
  })

  it('should handle multiple selections', async () => {
    render(<Filters onFilterChange={mockOnFilterChange} />)
    
    await waitFor(() => {
      expect(screen.getByText('BBC News')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByLabelText('BBC News'))
    fireEvent.click(screen.getByLabelText('CNN'))

    await waitFor(() => {
      expect(mockOnFilterChange).toHaveBeenLastCalledWith(
        expect.objectContaining({
          sources: expect.arrayContaining(['BBC News', 'CNN'])
        })
      )
    })
  })

  it('should deselect filter', async () => {
    render(<Filters onFilterChange={mockOnFilterChange} />)
    
    await waitFor(() => {
      expect(screen.getByText('BBC News')).toBeInTheDocument()
    })

    const checkbox = screen.getByLabelText('BBC News')
    
    // Select
    fireEvent.click(checkbox)
    // Deselect
    fireEvent.click(checkbox)

    await waitFor(() => {
      expect(mockOnFilterChange).toHaveBeenLastCalledWith(
        expect.objectContaining({
          sources: []
        })
      )
    })
  })

  it('should show clear all button when filters active', async () => {
    render(<Filters onFilterChange={mockOnFilterChange} />)
    
    await waitFor(() => {
      expect(screen.getByText('BBC News')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByLabelText('BBC News'))

    await waitFor(() => {
      expect(screen.getByText('Clear All')).toBeInTheDocument()
    })
  })

  it('should clear all filters', async () => {
    render(<Filters onFilterChange={mockOnFilterChange} />)
    
    await waitFor(() => {
      expect(screen.getByText('BBC News')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByLabelText('BBC News'))
    fireEvent.click(screen.getByLabelText('politics'))

    await waitFor(() => {
      expect(screen.getByText('Clear All')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Clear All'))

    await waitFor(() => {
      expect(mockOnFilterChange).toHaveBeenLastCalledWith({
        sources: [],
        categories: [],
        geographies: [],
        ideologies: []
      })
    })
  })

  it('should display selected count', async () => {
    render(<Filters onFilterChange={mockOnFilterChange} />)
    
    await waitFor(() => {
      expect(screen.getByText('BBC News')).toBeInTheDocument()
    })

    expect(screen.getByText(/Sources \(0 selected\)/)).toBeInTheDocument()

    fireEvent.click(screen.getByLabelText('BBC News'))

    await waitFor(() => {
      expect(screen.getByText(/Sources \(1 selected\)/)).toBeInTheDocument()
    })
  })
})
