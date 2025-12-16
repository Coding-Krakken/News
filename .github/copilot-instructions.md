# Copilot Instructions for News Analytics Platform

## Project Overview
- **Purpose**: Ingest news from multiple sources, cluster articles into stories, analyze coverage, and provide AI-powered fact-checking.
- **Major Components**:
  - **Backend** (`backend/app/`): FastAPI, MongoDB, NLP (Sentence Transformers), clustering (DBSCAN), OpenAI GPT for fact-checking.
  - **Frontend** (`frontend/src/`): React 18, Vite, custom CSS, Axios for API, hooks for state.

## Architecture & Data Flow
- **Ingestion**: Articles ingested from RSS/APIs → stored in MongoDB.
- **Clustering**: Articles grouped into stories using embeddings + DBSCAN.
- **Analytics**: Coverage stats by source, category, geography, time, ideology.
- **Fact-Checking**: AI extracts, corroborates, and classifies claims (confirmed/disputed/uncorroborated).
- **Frontend**: Fetches stories, analytics, and fact ledgers via REST API.

## Developer Workflows
- **Backend**:
  - Build: `cd backend && pip install -r requirements.txt`
  - Run: `uvicorn app.main:app --reload`
  - Test: `cd backend && ./run_tests.sh` (unit, integration, e2e; see `tests/README.md`)
- **Frontend**:
  - Build: `cd frontend && npm install && npm run build`
  - Run: `cd frontend && npm run dev`
  - Test: `cd frontend && ./run_tests.sh` (see `TEST_README.md`)
- **Full Stack**: Use `docker-compose.yml` for multi-service orchestration.

## Project-Specific Patterns & Conventions
- **Backend**:
  - API endpoints in `app/routes/`, business logic in `app/services/`, schemas in `app/models/schemas.py`.
  - Test structure: `tests/unit/`, `tests/integration/`, `tests/e2e/` (see `tests/README.md`).
  - Use dependency injection for services, mock external APIs in tests.
- **Frontend**:
  - Components in `src/components/`, pages in `src/pages/`, API logic in `src/services/api.js`.
  - Test files colocated in `src/__tests__/` and subfolders.
  - Use React hooks for state, avoid Redux.

## Integration & External Dependencies
- **MongoDB**: Required for backend data storage.
- **OpenAI API**: Needed for AI fact-checking (optional, but enables full functionality).
- **No hardcoded secrets**: Use environment variables for API keys and DB URIs.

## Examples
- **Add new API route**: Place in `app/routes/`, register in `main.py`, add service logic in `services/`, schema in `models/schemas.py`, and tests in `tests/integration/`.
- **Add frontend feature**: Create component in `src/components/`, page in `src/pages/`, update API calls in `src/services/api.js`, and add tests in `src/__tests__/`.

## References
- [README.md](../README.md): High-level overview
- [backend/tests/README.md](../backend/tests/README.md): Backend test details
- [frontend/TEST_README.md](../frontend/TEST_README.md): Frontend test details

---
For any unclear patterns or missing conventions, consult the referenced docs or ask for clarification.
