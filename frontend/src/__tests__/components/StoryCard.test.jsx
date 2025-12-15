import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import StoryCard from '../../components/StoryCard'

describe('StoryCard', () => {
  const mockStory = {
    story_id: 'story1',
    title: 'Test Story Title',
    summary: 'This is a test story summary',
    article_count: 5,
    category: 'politics',
    sources_covered: ['BBC News', 'CNN', 'Reuters']
  }

  const mockOnClick = vi.fn()

  it('should render story title', () => {
    render(<StoryCard story={mockStory} onClick={mockOnClick} />)
    expect(screen.getByText('Test Story Title')).toBeInTheDocument()
  })

  it('should render story summary', () => {
    render(<StoryCard story={mockStory} onClick={mockOnClick} />)
    expect(screen.getByText('This is a test story summary')).toBeInTheDocument()
  })

  it('should display article count', () => {
    render(<StoryCard story={mockStory} onClick={mockOnClick} />)
    expect(screen.getByText(/5 articles/)).toBeInTheDocument()
  })

  it('should display category badge', () => {
    render(<StoryCard story={mockStory} onClick={mockOnClick} />)
    expect(screen.getByText('politics')).toBeInTheDocument()
  })

  it('should display sources count', () => {
    render(<StoryCard story={mockStory} onClick={mockOnClick} />)
    expect(screen.getByText(/3 sources/)).toBeInTheDocument()
  })

  it('should display source badges', () => {
    render(<StoryCard story={mockStory} onClick={mockOnClick} />)
    expect(screen.getByText('BBC News')).toBeInTheDocument()
    expect(screen.getByText('CNN')).toBeInTheDocument()
    expect(screen.getByText('Reuters')).toBeInTheDocument()
  })

  it('should truncate sources when more than 5', () => {
    const storyWithManySources = {
      ...mockStory,
      sources_covered: ['Source1', 'Source2', 'Source3', 'Source4', 'Source5', 'Source6', 'Source7']
    }
    render(<StoryCard story={storyWithManySources} onClick={mockOnClick} />)
    expect(screen.getByText('+2 more')).toBeInTheDocument()
  })

  it('should call onClick when clicked', () => {
    render(<StoryCard story={mockStory} onClick={mockOnClick} />)
    const card = screen.getByText('Test Story Title').closest('.story-card')
    fireEvent.click(card)
    expect(mockOnClick).toHaveBeenCalledWith('story1')
  })

  it('should render without category', () => {
    const storyWithoutCategory = { ...mockStory, category: null }
    render(<StoryCard story={storyWithoutCategory} onClick={mockOnClick} />)
    expect(screen.getByText('Test Story Title')).toBeInTheDocument()
  })
})
