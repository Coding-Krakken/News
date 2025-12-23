import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import App from '../App'

// Mock the pages
vi.mock('../pages/StoriesPage', () => ({
  default: () => <div data-testid="stories-page">Stories Page</div>
}))

vi.mock('../pages/AnalyticsPage', () => ({
  default: () => <div data-testid="analytics-page">Analytics Page</div>
}))

describe('App', () => {
  it('should render header with title', () => {
    render(<App />)
    expect(screen.getByText('News Analytics Platform')).toBeInTheDocument()
  })

  it('should render header description', () => {
    render(<App />)
    expect(screen.getByText(/Ingest, cluster, and analyze news/)).toBeInTheDocument()
  })

  it('should render navigation buttons', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: /Stories/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Analytics/i })).toBeInTheDocument()
  })

  it('should show stories page by default', () => {
    render(<App />)
    expect(screen.getByTestId('stories-page')).toBeInTheDocument()
    expect(screen.queryByTestId('analytics-page')).not.toBeInTheDocument()
  })

  it('should switch to analytics page when button clicked', () => {
    render(<App />)
    
    const analyticsButton = screen.getByRole('button', { name: /Analytics/i })
    fireEvent.click(analyticsButton)
    
    expect(screen.getByTestId('analytics-page')).toBeInTheDocument()
    expect(screen.queryByTestId('stories-page')).not.toBeInTheDocument()
  })

  it('should switch back to stories page', () => {
    render(<App />)
    
    const analyticsButton = screen.getByRole('button', { name: /Analytics/i })
    const storiesButton = screen.getByRole('button', { name: /Stories/i })
    
    fireEvent.click(analyticsButton)
    expect(screen.getByTestId('analytics-page')).toBeInTheDocument()
    
    fireEvent.click(storiesButton)
    expect(screen.getByTestId('stories-page')).toBeInTheDocument()
    expect(screen.queryByTestId('analytics-page')).not.toBeInTheDocument()
  })

  it('should highlight active navigation button', () => {
    render(<App />)
    
    const storiesButton = screen.getByRole('button', { name: /Stories/i })
    const analyticsButton = screen.getByRole('button', { name: /Analytics/i })
    
    // Stories should be active by default
    expect(storiesButton).toHaveClass('active')
    expect(analyticsButton).not.toHaveClass('active')
    
    // Click analytics
    fireEvent.click(analyticsButton)
    expect(analyticsButton).toHaveClass('active')
    expect(storiesButton).not.toHaveClass('active')
  })
})
