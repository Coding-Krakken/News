import React, { useState } from "react";
import StoriesPage from "./pages/StoriesPage";
import AnalyticsPage from "./pages/AnalyticsPage";

function App() {
  const [currentPage, setCurrentPage] = useState("stories");

  return (
    <div>
      <header>
        <div className="container">
          <h1>News Analytics Platform</h1>
          <p>Ingest, cluster, and analyze news from multiple sources</p>

          <nav className="nav">
            <button
              className={currentPage === "stories" ? "active" : ""}
              onClick={() => setCurrentPage("stories")}
            >
              Stories
            </button>
            <button
              className={currentPage === "analytics" ? "active" : ""}
              onClick={() => setCurrentPage("analytics")}
            >
              Analytics
            </button>
          </nav>
        </div>
      </header>

      <div className="container">
        {currentPage === "stories" && <StoriesPage />}
        {currentPage === "analytics" && <AnalyticsPage />}
      </div>
    </div>
  );
}

export default App;
