import axios from 'axios';

const API_BASE_URL = '/api';

export const articleService = {
  ingestArticles: async () => {
    const response = await axios.post(`${API_BASE_URL}/articles/ingest`);
    return response.data;
  },

  getArticles: async (params = {}) => {
    const response = await axios.get(`${API_BASE_URL}/articles/`, { params });
    return response.data;
  },

  getSources: async () => {
    const response = await axios.get(`${API_BASE_URL}/articles/sources/list`);
    return response.data;
  }
};

export const storyService = {
  clusterStories: async () => {
    const response = await axios.post(`${API_BASE_URL}/stories/cluster`);
    return response.data;
  },

  getStories: async (params = {}) => {
    const response = await axios.get(`${API_BASE_URL}/stories/`, { params });
    return response.data;
  },

  getStory: async (storyId) => {
    const response = await axios.get(`${API_BASE_URL}/stories/${storyId}`);
    return response.data;
  },

  getStoryArticles: async (storyId) => {
    const response = await axios.get(`${API_BASE_URL}/stories/${storyId}/articles`);
    return response.data;
  },

  getStoryCoverage: async (storyId) => {
    const response = await axios.get(`${API_BASE_URL}/stories/${storyId}/coverage`);
    return response.data;
  }
};

export const analyticsService = {
  getStats: async () => {
    const response = await axios.get(`${API_BASE_URL}/analytics/stats`);
    return response.data;
  },

  filterArticles: async (filters) => {
    const response = await axios.get(`${API_BASE_URL}/analytics/filter`, { params: filters });
    return response.data;
  },

  getFacets: async () => {
    const response = await axios.get(`${API_BASE_URL}/analytics/facets`);
    return response.data;
  }
};

export const factCheckerService = {
  generateFactLedger: async (storyId) => {
    const response = await axios.post(`${API_BASE_URL}/fact-checker/${storyId}`);
    return response.data;
  },

  getFactLedger: async (storyId) => {
    const response = await axios.get(`${API_BASE_URL}/fact-checker/${storyId}`);
    return response.data;
  }
};
