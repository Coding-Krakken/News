ADR 0002 — Tool Versions and Pinning

Status: Proposed
Date: 2025-12-26

Decision
- Pin primary developer tool versions to reduce CI drift and ensure reproducible behavior.

Pinned tools (initial):
- `black` = 24.1.0
- `ruff` = 0.0.262 (via ruff-pre-commit)
- `markdownlint-cli` = 0.35.0 (CI)
- Node.js = 18 (CI)
- Python = 3.12 (CI)

Rationale
- Pinning prevents unexpected linter/formatter behavior changes and maintains deterministic CI.

Consequences
- CI and local developer environments must use these versions. Add pre-commit and CI checks to enforce.

READY FOR IMPLEMENTATION
