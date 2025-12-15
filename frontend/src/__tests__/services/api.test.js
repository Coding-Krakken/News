import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import {
  articleService,
  storyService,
  analyticsService,
  factCheckerService
} from '../../services/api'

// Mock axios
vi.mock('axios')

describe('API Services', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('articleService', () => {
    it('should ingest articles', async () => {
      const mockResponse = { data: { total_ingested: 10, total_sources: 4 } }
      axios.post.mockResolvedValue(mockResponse)

      const result = await articleService.ingestArticles()

      expect(axios.post).toHaveBeenCalledWith('/api/articles/ingest')
      expect(result).toEqual(mockResponse.data)
    })

    it('should get articles with parameters', async () => {
      const mockArticles = [{ title: 'Test Article' }]
      axios.get.mockResolvedValue({ data: mockArticles })

      const result = await articleService.getArticles({ skip: 0, limit: 10 })

      expect(axios.get).toHaveBeenCalledWith('/api/articles/', {
        params: { skip: 0, limit: 10 }
      })
      expect(result).toEqual(mockArticles)
    })

    it('should get sources', async () => {
      const mockSources = [{ name: 'BBC News' }, { name: 'CNN' }]
      axios.get.mockResolvedValue({ data: mockSources })

      const result = await articleService.getSources()

      expect(axios.get).toHaveBeenCalledWith('/api/articles/sources/list')
      expect(result).toEqual(mockSources)
    })
  })

  describe('storyService', () => {
    it('should cluster stories', async () => {
      const mockResponse = { data: { message: 'Clustering started' } }
      axios.post.mockResolvedValue(mockResponse)

      const result = await storyService.clusterStories()

      expect(axios.post).toHaveBeenCalledWith('/api/stories/cluster')
      expect(result).toEqual(mockResponse.data)
    })

    it('should get stories', async () => {
      const mockStories = [{ story_id: '1', title: 'Test Story' }]
      axios.get.mockResolvedValue({ data: mockStories })

      const result = await storyService.getStories()

      expect(axios.get).toHaveBeenCalledWith('/api/stories/', { params: {} })
      expect(result).toEqual(mockStories)
    })

    it('should get story by id', async () => {
      const mockStory = { story_id: '1', title: 'Test Story' }
      axios.get.mockResolvedValue({ data: mockStory })

      const result = await storyService.getStory('1')

      expect(axios.get).toHaveBeenCalledWith('/api/stories/1')
      expect(result).toEqual(mockStory)
    })

    it('should get story articles', async () => {
      const mockArticles = [{ title: 'Article 1' }]
      axios.get.mockResolvedValue({ data: mockArticles })

      const result = await storyService.getStoryArticles('1')

      expect(axios.get).toHaveBeenCalledWith('/api/stories/1/articles')
      expect(result).toEqual(mockArticles)
    })

    it('should get story coverage', async () => {
      const mockCoverage = { coverage_percentage: 75 }
      axios.get.mockResolvedValue({ data: mockCoverage })

      const result = await storyService.getStoryCoverage('1')

      expect(axios.get).toHaveBeenCalledWith('/api/stories/1/coverage')
      expect(result).toEqual(mockCoverage)
    })
  })

  describe('analyticsService', () => {
    it('should get stats', async () => {
      const mockStats = { total_articles: 100, total_stories: 20 }
      axios.get.mockResolvedValue({ data: mockStats })

      const result = await analyticsService.getStats()

      expect(axios.get).toHaveBeenCalledWith('/api/analytics/stats')
      expect(result).toEqual(mockStats)
    })

    it('should filter articles', async () => {
      const mockArticles = [{ title: 'Filtered Article' }]
      axios.get.mockResolvedValue({ data: mockArticles })

      const filters = { sources: 'BBC News,CNN' }
      const result = await analyticsService.filterArticles(filters)

      expect(axios.get).toHaveBeenCalledWith('/api/analytics/filter', {
        params: filters
      })
      expect(result).toEqual(mockArticles)
    })

    it('should get facets', async () => {
      const mockFacets = { sources: ['BBC'], categories: ['politics'] }
      axios.get.mockResolvedValue({ data: mockFacets })

      const result = await analyticsService.getFacets()

      expect(axios.get).toHaveBeenCalledWith('/api/analytics/facets')
      expect(result).toEqual(mockFacets)
    })
  })

  describe('factCheckerService', () => {
    it('should generate fact ledger', async () => {
      const mockLedger = { confirmed_claims: [], disputed_claims: [] }
      axios.post.mockResolvedValue({ data: mockLedger })

      const result = await factCheckerService.generateFactLedger('story1')

      expect(axios.post).toHaveBeenCalledWith('/api/fact-checker/story1')
      expect(result).toEqual(mockLedger)
    })

    it('should get fact ledger', async () => {
      const mockLedger = { confirmed_claims: [], disputed_claims: [] }
      axios.get.mockResolvedValue({ data: mockLedger })

      const result = await factCheckerService.getFactLedger('story1')

      expect(axios.get).toHaveBeenCalledWith('/api/fact-checker/story1')
      expect(result).toEqual(mockLedger)
    })
  })
})
