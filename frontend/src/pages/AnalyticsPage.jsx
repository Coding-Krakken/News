import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/api';

function AnalyticsPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await analyticsService.getStats();
      setStats(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!stats) {
    return <div className="empty-state">No data available</div>;
  }

  return (
    <div>
      <h2 style={{ marginBottom: '20px' }}>Coverage Analytics</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Overview</h3>
          <ul className="stat-list">
            <li>
              <span>Total Articles</span>
              <strong>{stats.total_articles}</strong>
            </li>
            <li>
              <span>Total Stories</span>
              <strong>{stats.total_stories}</strong>
            </li>
          </ul>
        </div>

        <div className="stat-card">
          <h3>By Source</h3>
          <ul className="stat-list">
            {Object.entries(stats.by_source).map(([source, count]) => (
              <li key={source}>
                <span>{source}</span>
                <strong>{count}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="stat-card">
          <h3>By Category</h3>
          <ul className="stat-list">
            {Object.entries(stats.by_category).length > 0 ? (
              Object.entries(stats.by_category).map(([category, count]) => (
                <li key={category}>
                  <span>{category}</span>
                  <strong>{count}</strong>
                </li>
              ))
            ) : (
              <li><span>No categories available</span></li>
            )}
          </ul>
        </div>

        <div className="stat-card">
          <h3>By Geography</h3>
          <ul className="stat-list">
            {Object.entries(stats.by_geography).map(([geo, count]) => (
              <li key={geo}>
                <span>{geo}</span>
                <strong>{count}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="stat-card">
          <h3>By Ideology</h3>
          <ul className="stat-list">
            {Object.entries(stats.by_ideology).map(([ideology, count]) => (
              <li key={ideology}>
                <span>{ideology}</span>
                <strong>{count}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="stat-card">
          <h3>By Time</h3>
          <ul className="stat-list">
            {Object.entries(stats.by_time).map(([time, count]) => (
              <li key={time}>
                <span>{time}</span>
                <strong>{count}</strong>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsPage;
