import React, { useState, useEffect } from 'react';
import { filterService } from '../services/filterService';
import { SavedFilter } from '../types';

export function FiltersPage() {
  const [filters, setFilters] = useState<SavedFilter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [filterQuery, setFilterQuery] = useState('');

  useEffect(() => {
    loadFilters();
  }, []);

  const loadFilters = async () => {
    try {
      const data = await filterService.list();
      setFilters(data);
    } catch (err: unknown) {
      type ErrorResponse = { response?: { data?: { error?: string } } };
      const msg = (err as ErrorResponse)?.response?.data?.error || 'Failed to load filters';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const query = JSON.parse(filterQuery);
      const newFilter = await filterService.create(name, query);
      setFilters([...filters, newFilter]);
      setName('');
      setFilterQuery('');
      setShowForm(false);
    } catch (err: unknown) {
      type ErrorResponse = { response?: { data?: { error?: string } } };
      const msg = (err as ErrorResponse)?.response?.data?.error || 'Failed to create filter';
      alert(msg);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await filterService.delete(id);
      setFilters(filters.filter(f => f.id !== id));
    } catch (err: unknown) {
      type ErrorResponse = { response?: { data?: { error?: string } } };
      const msg = (err as ErrorResponse)?.response?.data?.error || 'Failed to delete filter';
      alert(msg);
    }
  };

  if (loading) {
    return <div>Loading filters...</div>;
  }

  return (
    <div className="filters-page">
      <h1>Saved Filters</h1>
      {error && <div className="error">{error}</div>}
      
      <button onClick={() => setShowForm(!showForm)}>
        {showForm ? 'Cancel' : 'Add New Filter'}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="name">Filter Name:</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="filterQuery">Filter Query (JSON):</label>
            <textarea
              id="filterQuery"
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              placeholder='{"category": "tech", "language": "en"}'
              required
            />
          </div>
          <button type="submit">Save Filter</button>
        </form>
      )}

      {filters.length === 0 ? (
        <p>No saved filters yet</p>
      ) : (
        <ul>
          {filters.map(filter => (
            <li key={filter.id}>
              <h3>{filter.name}</h3>
              <pre>{JSON.stringify(filter.filter_query, null, 2)}</pre>
              <button onClick={() => handleDelete(filter.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
