STANDARDS — Copilot Multi-Agent Engineering System

Principles (Non-negotiable)
- ONE APPROACH RULE: pick the single best pattern per concern and apply it consistently across the repo.
- DESIGN FIRST: every change requires a written plan (one-paragraph minimum) before code.
- SMALL, REVIEWABLE DIFFS: aim for PRs under ~400 lines of net change.

Testing
- Coverage: 100% coverage for all new and modified code (unit, integration, e2e as applicable).
- Determinism: tests must be deterministic and fast. No sleeps, randomness, or external network without mocks.
- Test artifacts: each PR adds tests that fail before the change and pass after.

Security
- Secrets: never commit secrets. Use environment variables and secret stores.
- Least privilege for credentials and CI tokens.
- Dependencies: require automated dependency checks and quarterly dependency audits.

CI / Release
- CI must be deterministic: pinned tool versions, lockfiles, cached artifacts.
- Release gating: tests + security + performance checks must pass before releases.

Performance & Reliability
- Define SLOs and budgets for new features.
- Add lightweight benchmarks for critical paths and guardrails for regressions.

Docs & DX
- Every behavioral change must update docs (README, ADRs, or docs folder).
- Provide runnable examples and quick-start commands.

Coding
- Strong typing where applicable. Prefer explicit error handling over silent fallbacks.
- No commented-out code left in PRs.

PR Etiquette
- PR description must contain: what changed, why, how to test, rollout notes, risks.
- Link design doc or ADR for non-trivial changes.

Observability
- Add logs/metrics for new long-running or failure-prone operations.

ADR Process
- Use `docs/ADR/` for records. New major decisions require an ADR.

Related knowledge files
- Coding style: `docs/CODING_STYLE.md`
- Docs style: `docs/DOCS_STYLE.md`
- SOPs: `docs/SOPs/REVIEW_SOP.md`, `docs/SOPs/RELEASE_SOP.md`, `docs/SOPs/SECURITY_SOP.md`, `docs/SOPs/PERFORMANCE_SOP.md`, `docs/SOPs/TESTING_SOP.md`
- Agent usage: `docs/AGENTS_README.md`

READY FOR IMPLEMENTATION
