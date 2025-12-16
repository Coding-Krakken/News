import { apiClient } from './apiClient';
import { SavedFilter } from '../types';

export const filterService = {
  async create(name: string, filterQuery: Record<string, any>): Promise<SavedFilter> {
    const response = await apiClient.post<{ filter: SavedFilter }>('/saved-filters', {
      name,
      filter_query: filterQuery,
    });
    return response.data.filter;
  },

  async list(): Promise<SavedFilter[]> {
    const response = await apiClient.get<{ filters: SavedFilter[] }>('/saved-filters');
    return response.data.filters;
  },

  async update(id: number, data: Partial<SavedFilter>): Promise<SavedFilter> {
    const response = await apiClient.put<{ filter: SavedFilter }>(`/saved-filters/${id}`, data);
    return response.data.filter;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/saved-filters/${id}`);
  },
};
