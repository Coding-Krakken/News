import React from 'react';

function StoryCard({ story, onClick }) {
  return (
    <div className="story-card" onClick={() => onClick(story.story_id)}>
      <h3>{story.title}</h3>
      <p>{story.summary}</p>
      
      <div className="story-meta">
        <span className="badge badge-primary">{story.article_count} articles</span>
        {story.category && <span className="badge badge-secondary">{story.category}</span>}
        <span className="badge badge-success">
          {story.sources_covered.length} sources
        </span>
      </div>
      
      <div className="coverage-matrix">
        <h4>Sources:</h4>
        <div className="coverage-list">
          {story.sources_covered.slice(0, 5).map(source => (
            <span key={source} className="coverage-badge covered">
              {source}
            </span>
          ))}
          {story.sources_covered.length > 5 && (
            <span className="coverage-badge covered">
              +{story.sources_covered.length - 5} more
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default StoryCard;
