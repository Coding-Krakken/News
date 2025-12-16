# Copilot Instructions for News Analytics Platform

## Golden Standards (Non-Negotiable)

These standards are required for every change. If any standard cannot be met, stop and explain why, then propose the smallest viable plan to meet it.

### 1) Quality Gates (Must Pass)
- ✅ Typecheck passes (no `any` creep / no suppressed errors).
- ✅ Lint passes (no new warnings).
- ✅ Build passes.
- ✅ All tests pass (unit + integration + e2e where applicable).
- ✅ Coverage meets the policy (see Testing & Coverage).
- ✅ No secrets or credentials committed.
- ✅ Docs updated (README / ADR / in-code docs) when behavior changes.
- ✅ Observability updated (logs/metrics/traces) when behavior changes.

### 2) Testing & Coverage (Hard Requirement)
- **100% coverage across the entire application** (lines/branches/functions/statements).
- Coverage must be enforced in CI; merges are blocked if coverage drops below 100%.
- “Coverage” means: critical paths, edge cases, and error paths are tested—not just executed.
- Each PR must include:
  - new/updated tests for new behavior
  - regression tests for fixed bugs
  - at least one negative test (failure/invalid input) for each new API or feature

#### Test Pyramid (Required)
- **Unit tests:** pure logic, utilities, reducers, validators, formatters, domain rules.
- **Integration tests:** DB + API + service layer; realistic flows; contract validations.
- **E2E tests (Playwright):** user-visible workflows; major routes; auth/RBAC boundaries.
- Prefer **more unit/integration** over E2E, but E2E must cover critical user journeys.

#### Golden Testing Rules
- Tests must be deterministic: no random timers, no reliance on external services.
- Mock only at system boundaries (3rd party APIs). Prefer real implementations internally.
- Use test factories/fixtures; avoid copy-paste test setup.
- Every bug fix must add a test that fails before the fix and passes after.
- If a test is flaky, fix it immediately—never “skip” or “quarantine” without a plan.

### 3) Architecture & Consistency Standards
- Pick ONE approach per concern and apply it everywhere:
  - validation strategy
  - error handling pattern
  - logging pattern
  - data access strategy
  - routing conventions
  - naming conventions
- No parallel patterns that do the same thing in different places.
- Keep layers clean:
  - UI (rendering) ↔ Service/Domain (logic) ↔ Data (DB/IO)
- Avoid cross-contamination of roles (e.g., driver UI must not leak admin capabilities).

### 4) Code Standards (Google/Microsoft-style)
- Small, readable functions with clear names.
- No “clever” code. Prefer clarity and explicitness.
- Strong typing everywhere; avoid `any`, unsafe casts, and silent fallbacks.
- Idempotent operations where relevant; safe retries; predictable side effects.
- Explicit input validation at every API boundary.
- Stable, well-defined error contracts (consistent status codes + error shapes).
- No dead code; remove unused exports, files, flags, and commented-out blocks.

### 5) Security Standards
- Principle of least privilege (RBAC enforced server-side).
- Validate + sanitize all external input.
- Secure session/auth handling; avoid leaking sensitive info in logs/errors.
- Rate limit and abuse-protect public endpoints.
- Dependency hygiene: fix vulnerable packages, lockfile maintained, no abandoned deps without reason.

### 6) Performance & Reliability Standards
- Avoid N+1 queries and unnecessary client-side fetch loops.
- Prefer caching where appropriate; ensure cache invalidation is correct.
- Keep UI responsive: loading states, skeletons, and optimistic updates where suitable.
- Add instrumentation for slow operations and failures.
- Ensure graceful degradation and helpful error UX.

### 7) Documentation Standards
- Update docs when behavior, API, env vars, setup, or workflows change.
- Add ADRs for major decisions (why we chose X over Y).
- Keep a “How to test locally” section accurate and complete.

### 8) PR / Change Management Standards
- PRs must be small enough to review quickly; split large efforts.
- Every PR description must include:
  - what changed
  - why
  - how to test
  - risks/rollout notes
- Prefer refactors that improve clarity, reduce duplication, and increase coverage.

### 9) Copilot Operating Rules (How you should behave)
- Before coding: scan the codebase for existing patterns and reuse them.
- If multiple solutions are possible: choose ONE best approach and make everything else match it.
- Do not add new libraries unless necessary; justify additions.
- Do not “paper over” issues with try/catch or silent fallbacks.
- If anything is ambiguous: make the safest assumption and implement with guardrails + tests.

(See <attachments> above for file contents. You may not need to search or read the file again.)

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
