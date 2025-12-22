import React, { useState, useEffect } from 'react';
import { storyService, articleService } from '../services/api';
import StoryCard from '../components/StoryCard';
import StoryDetail from '../components/StoryDetail';
import Filters from '../components/Filters';

function StoriesPage() {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStory, setSelectedStory] = useState(null);
  const [ingesting, setIngesting] = useState(false);
  const [clustering, setClustering] = useState(false);

  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      setLoading(true);
      const data = await storyService.getStories();
      setStories(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleIngest = async () => {
    try {
      setIngesting(true);
      await articleService.ingestArticles();
      setIngesting(false);
      alert('Articles ingested successfully! Now cluster them to create stories.');
    } catch (err) {
      setError(err.message);
      setIngesting(false);
    }
  };

  const handleCluster = async () => {
    try {
      setClustering(true);
      await storyService.clusterStories();
      // Wait a bit for clustering to complete
      setTimeout(() => {
        loadStories();
        setClustering(false);
      }, 3000);
    } catch (err) {
      setError(err.message);
      setClustering(false);
    }
  };

  const handleFilterChange = (filters) => {
    // In a real app, you would filter stories based on selected filters
    console.log('Filters changed:', filters);
  };

  if (selectedStory) {
    return <StoryDetail storyId={selectedStory} onClose={() => setSelectedStory(null)} />;
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button 
          onClick={handleIngest} 
          className="button button-primary"
          disabled={ingesting}
        >
          {ingesting ? 'Ingesting...' : 'Ingest Articles'}
        </button>
        <button 
          onClick={handleCluster} 
          className="button button-primary"
          disabled={clustering}
        >
          {clustering ? 'Clustering...' : 'Cluster Stories'}
        </button>
        <button 
          onClick={loadStories} 
          className="button button-secondary"
        >
          Refresh
        </button>
      </div>

      <Filters onFilterChange={handleFilterChange} />

      {error && <div className="error">Error: {error}</div>}

      {loading ? (
        <div className="loading">Loading stories...</div>
      ) : stories.length === 0 ? (
        <div className="empty-state">
          <h3>No stories yet</h3>
          <p>Ingest articles and cluster them to see stories here.</p>
        </div>
      ) : (
        <div className="stories-grid">
          {stories.map(story => (
            <StoryCard 
              key={story.story_id} 
              story={story} 
              onClick={setSelectedStory}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default StoriesPage;
