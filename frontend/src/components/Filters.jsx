import React, { useState, useEffect } from "react";
import { analyticsService } from "../services/api";

function Filters({ onFilterChange }) {
  const [facets, setFacets] = useState({
    sources: [],
    categories: [],
    geographies: [],
    ideologies: [],
  });
  const [selectedFilters, setSelectedFilters] = useState({
    sources: [],
    categories: [],
    geographies: [],
    ideologies: [],
  });

  useEffect(() => {
    loadFacets();
  }, []);

  const loadFacets = async () => {
    try {
      const data = await analyticsService.getFacets();
      setFacets(data);
    } catch (err) {
      console.error("Error loading facets:", err);
    }
  };

  const handleCheckboxChange = (filterType, value) => {
    setSelectedFilters((prev) => {
      const current = prev[filterType];
      const updated = current.includes(value)
        ? current.filter((v) => v !== value)
        : [...current, value];

      const newFilters = { ...prev, [filterType]: updated };
      onFilterChange(newFilters);
      return newFilters;
    });
  };

  const clearFilters = () => {
    const emptyFilters = {
      sources: [],
      categories: [],
      geographies: [],
      ideologies: [],
    };
    setSelectedFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const hasActiveFilters = Object.values(selectedFilters).some(
    (arr) => arr.length > 0,
  );

  return (
    <div className="filters">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "15px",
        }}
      >
        <h3>Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="button button-secondary"
            style={{ padding: "6px 12px" }}
          >
            Clear All
          </button>
        )}
      </div>

      {facets.sources.length > 0 && (
        <div className="filter-section">
          <label>Sources ({selectedFilters.sources.length} selected)</label>
          <div className="checkbox-group">
            {facets.sources.map((source) => (
              <div key={source} className="checkbox-item">
                <input
                  type="checkbox"
                  id={`source-${source}`}
                  checked={selectedFilters.sources.includes(source)}
                  onChange={() => handleCheckboxChange("sources", source)}
                />
                <label htmlFor={`source-${source}`}>{source}</label>
              </div>
            ))}
          </div>
        </div>
      )}

      {facets.categories.length > 0 && (
        <div className="filter-section">
          <label>
            Categories ({selectedFilters.categories.length} selected)
          </label>
          <div className="checkbox-group">
            {facets.categories.map((category) => (
              <div key={category} className="checkbox-item">
                <input
                  type="checkbox"
                  id={`category-${category}`}
                  checked={selectedFilters.categories.includes(category)}
                  onChange={() => handleCheckboxChange("categories", category)}
                />
                <label htmlFor={`category-${category}`}>{category}</label>
              </div>
            ))}
          </div>
        </div>
      )}

      {facets.geographies.length > 0 && (
        <div className="filter-section">
          <label>
            Geography ({selectedFilters.geographies.length} selected)
          </label>
          <div className="checkbox-group">
            {facets.geographies.map((geo) => (
              <div key={geo} className="checkbox-item">
                <input
                  type="checkbox"
                  id={`geo-${geo}`}
                  checked={selectedFilters.geographies.includes(geo)}
                  onChange={() => handleCheckboxChange("geographies", geo)}
                />
                <label htmlFor={`geo-${geo}`}>{geo}</label>
              </div>
            ))}
          </div>
        </div>
      )}

      {facets.ideologies.length > 0 && (
        <div className="filter-section">
          <label>Ideology ({selectedFilters.ideologies.length} selected)</label>
          <div className="checkbox-group">
            {facets.ideologies.map((ideology) => (
              <div key={ideology} className="checkbox-item">
                <input
                  type="checkbox"
                  id={`ideology-${ideology}`}
                  checked={selectedFilters.ideologies.includes(ideology)}
                  onChange={() => handleCheckboxChange("ideologies", ideology)}
                />
                <label htmlFor={`ideology-${ideology}`}>{ideology}</label>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Filters;
