import React, { useState, useEffect } from 'react';
import { storyService, factCheckerService } from '../services/api';

function StoryDetail({ storyId, onClose }) {
  const [story, setStory] = useState(null);
  const [articles, setArticles] = useState([]);
  const [coverage, setCoverage] = useState(null);
  const [factLedger, setFactLedger] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingFacts, setGeneratingFacts] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStoryDetails();
  }, [storyId]);

  const loadStoryDetails = async () => {
    try {
      setLoading(true);
      const [storyData, articlesData, coverageData] = await Promise.all([
        storyService.getStory(storyId),
        storyService.getStoryArticles(storyId),
        storyService.getStoryCoverage(storyId)
      ]);
      
      setStory(storyData);
      setArticles(articlesData);
      setCoverage(coverageData);
      
      // Try to load existing fact ledger
      try {
        const ledger = await factCheckerService.getFactLedger(storyId);
        setFactLedger(ledger);
      } catch (err) {
        // Fact ledger doesn't exist yet
      }
      
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const generateFactLedger = async () => {
    try {
      setGeneratingFacts(true);
      const ledger = await factCheckerService.generateFactLedger(storyId);
      setFactLedger(ledger);
      setGeneratingFacts(false);
    } catch (err) {
      setError(err.message);
      setGeneratingFacts(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading story details...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="story-detail">
      <button onClick={onClose} className="button button-secondary" style={{ marginBottom: '20px' }}>
        ← Back to Stories
      </button>
      
      <div className="story-card" style={{ marginBottom: '20px' }}>
        <h2>{story.title}</h2>
        <p>{story.summary}</p>
        
        <div className="story-meta">
          <span className="badge badge-primary">{story.article_count} articles</span>
          {story.category && <span className="badge badge-secondary">{story.category}</span>}
        </div>
        
        {coverage && (
          <div className="coverage-matrix">
            <h4>Coverage by Source ({coverage.sources_covered.length} sources covered)</h4>
            <div className="coverage-list">
              {Object.entries(coverage.coverage).map(([source, covered]) => (
                <span key={source} className={`coverage-badge ${covered ? 'covered' : 'not-covered'}`}>
                  {source} {covered ? '✓' : '✗'}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div className="story-card" style={{ marginBottom: '20px' }}>
        <h3>Articles in this Story</h3>
        {articles.map((article, idx) => (
          <div key={idx} style={{ padding: '10px 0', borderBottom: '1px solid #eee' }}>
            <strong>{article.source_name}</strong>: {article.title}
            <br />
            <small style={{ color: '#666' }}>
              {new Date(article.published_date).toLocaleString()}
            </small>
          </div>
        ))}
      </div>
      
      <div className="story-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>Fact-Only Analysis</h3>
          {!factLedger && (
            <button 
              onClick={generateFactLedger} 
              className="button button-primary"
              disabled={generatingFacts}
            >
              {generatingFacts ? 'Generating...' : 'Generate Fact Ledger'}
            </button>
          )}
        </div>
        
        {factLedger ? (
          <div className="fact-ledger">
            {factLedger.confirmed_claims.length > 0 && (
              <div className="claims-section">
                <h4>✓ Confirmed Claims ({factLedger.confirmed_claims.length})</h4>
                {factLedger.confirmed_claims.map((claim, idx) => (
                  <div key={idx} className="claim confirmed">
                    <div className="claim-text">{claim.text}</div>
                    <div className="claim-meta">
                      Originally from: {claim.attribution} | 
                      Corroborated by {claim.corroboration_count} sources: {claim.supporting_sources.join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {factLedger.disputed_claims.length > 0 && (
              <div className="claims-section">
                <h4>✗ Disputed Claims ({factLedger.disputed_claims.length})</h4>
                {factLedger.disputed_claims.map((claim, idx) => (
                  <div key={idx} className="claim disputed">
                    <div className="claim-text">{claim.text}</div>
                    <div className="claim-meta">
                      From: {claim.attribution} | 
                      Disputed by: {claim.disputing_sources.join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {factLedger.uncorroborated_claims.length > 0 && (
              <div className="claims-section">
                <h4>? Uncorroborated Claims ({factLedger.uncorroborated_claims.length})</h4>
                {factLedger.uncorroborated_claims.map((claim, idx) => (
                  <div key={idx} className="claim uncorroborated">
                    <div className="claim-text">{claim.text}</div>
                    <div className="claim-meta">
                      From: {claim.attribution} | No corroboration from other sources
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p style={{ color: '#666' }}>
            Click "Generate Fact Ledger" to analyze all sources, extract claims, 
            cross-corroborate them, and separate confirmed from disputed facts.
          </p>
        )}
      </div>
    </div>
  );
}

export default StoryDetail;
