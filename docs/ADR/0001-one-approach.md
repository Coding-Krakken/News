ADR 0001 — ONE APPROACH RULE: Repository-wide single-pattern choices

Status: Proposed
Date: 2025-12-26

Context
- This repository must be maintainable by distributed, parallel agents and humans.
- Multiple competing approaches increase cognitive load, cause CI flakiness, and hinder deterministic automation.

Decision
- Adopt a repository-wide "ONE APPROACH" policy: pick a single, explicit approach per concern and apply it consistently.

Chosen approaches (initial set)
- Python: Async-first services use `async`/`await` and Motor for MongoDB where applicable.
- Python formatting/linting: `black` for formatting, `ruff` for linting and simple fixes.
- JS/TS: Strict TypeScript, `prettier` + `eslint` with project configuration.
- Tests: Tests-first for non-trivial logic; 100% coverage required for changed files.
- Docs: `markdownlint` in CI; docs must include Quick Start and runnable examples.

Rationale
- Single patterns reduce review time and make automated agents' behavior deterministic.
- Enforcing formatters/linters in CI reduces formatting churn and merge conflicts.

Consequences
- Short-term: some refactors required to conform to chosen tools.
- Long-term: easier automation, fewer style debates, reliable CI.

Alternatives considered
- Allow multiple patterns per language — rejected due to increased complexity.

Notes
- This ADR can be revised; changes require a follow-up ADR documenting why the approach changed and migration plan.

READY FOR IMPLEMENTATION
