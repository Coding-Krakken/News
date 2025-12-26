Agents README — How to use the Copilot Agent Team

Purpose

- Quick reference for working with the repo-integrated agent team.

Where files live

- Agent prompts: `.github/prompts/*.agent.md`
- Standards: `docs/STANDARDS.md`
- SOPs: `docs/SOPs/*.md`

Quick workflow

1. Tech Lead produces a plan and hands off to Implementation with a copy-paste box.
2. Implementation opens small PR(s), includes tests, and uses `.github/pull_request_template.md`.
3. Run parallel reviews: QA → Security → Performance → Docs using the provided handoff boxes.
4. CI/Release runs final gating and approves or blocks merge.

## Handoff box (mandatory format)

## 📦 COPY & PASTE — <AGENT NAME>

## <minimal, precise task prompt>

References

- `docs/STANDARDS.md`, `docs/CODING_STYLE.md`, `docs/DOCS_STYLE.md`, `docs/SOPs/`

Ready
