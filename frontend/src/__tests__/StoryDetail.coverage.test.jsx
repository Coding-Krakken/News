import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import StoryDetail from '../../components/StoryDetail'

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

import { storyService, factCheckerService } from '../../services/api'

describe('StoryDetail coverage additions', () => {
  const mockStory = {
    story_id: 's1',
    title: 'Coverage Story',
    summary: 'Coverage summary',
    article_count: 2,
    category: 'world'
  }

  const mockArticles = [
    { source_name: 'A', title: 'A1', published_date: new Date().toISOString() }
  ]

  const mockCoverage = {
    coverage: { A: true },
    sources_covered: ['A']
  }

  const fullLedger = {
    confirmed_claims: [
      { text: 'C1', attribution: 'A', supporting_sources: ['A'], corroboration_count: 1 }
    ],
    disputed_claims: [
      { text: 'D1', attribution: 'B', disputing_sources: ['C'] }
    ],
    uncorroborated_claims: [
      { text: 'U1', attribution: 'D' }
    ]
  }

  beforeEach(() => {
    vi.clearAllMocks()
    storyService.getStory.mockResolvedValue(mockStory)
    storyService.getStoryArticles.mockResolvedValue(mockArticles)
    storyService.getStoryCoverage.mockResolvedValue(mockCoverage)
  })

  it('renders all claim sections when ledger contains all types', async () => {
    factCheckerService.getFactLedger.mockResolvedValue(fullLedger)

    render(<StoryDetail storyId="s1" onClose={() => {}} />)

    await waitFor(() => expect(screen.getByText('Coverage Story')).toBeInTheDocument())

    // Confirm all three sections are rendered
    expect(screen.getByText(/Confirmed Claims/)).toBeInTheDocument()
    expect(screen.getByText(/Disputed Claims/)).toBeInTheDocument()
    expect(screen.getByText(/Uncorroborated Claims/)).toBeInTheDocument()
  })
})
