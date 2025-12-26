Testing SOP

Purpose

- Ensure deterministic, fast, and complete test coverage.

Rules

- 100% coverage for new and modified code. Tests must be deterministic.
- Unit tests cover logic, integration tests cover DB + API, e2e cover user flows.
- Mock external services; use deterministic fixtures and time-freeze patterns.

Enforcement

- CI enforces coverage thresholds and runs with fixed tool versions.

Ready
