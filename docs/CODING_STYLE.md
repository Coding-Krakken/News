Coding Style & Conventions

Purpose

- Provide concise, consistent coding conventions for all languages in this repo.

General

- ONE approach per concern. If the repo already uses a style, follow it.
- Keep functions small (< 80 lines), pure where possible, explicit error handling.
- No single-letter variable names except common counters (i, j) in small scopes.

Python

- Use type hints for all public functions and dataclasses.
- Use `black` for formatting and `ruff`/`flake8` for linting rules.
- Exceptions: prefer explicit exception types and avoid bare `except`.

TypeScript / JS

- Use `prettier` for formatting, `eslint` with strict rules, and `tsc` for type checks.

Commits & PRs

- Commit messages: `scope: short description` (imperative). Include ticket/issue if applicable.
- PRs: small, single-purpose, and follow `.github/pull_request_template.md`.

Testing

- Tests first for non-trivial logic. Aim for small, deterministic unit tests.

Documentation

- Update relevant docs for any behavior change. Examples must be runnable.

Ready
