PR Review SOP

Purpose
- Standardize PR review behavior for speed and quality.

Steps for reviewer
1. Confirm PR uses `.github/pull_request_template.md` and references Tech Lead plan or ADR.
2. Run local quick checks: `./run_tests.sh` and linters for target language.
3. Read the design summary and acceptance criteria.
4. Focus review on correctness, testing coverage, security, and performance risks.
5. Approve small PRs within 24 hours; request changes if issues found.

Merge rules
- All domain agents (QA, Security, Performance, Docs) must sign off in PR comments.
- CI must be green and coverage must meet `docs/STANDARDS.md` requirements.

Ready
