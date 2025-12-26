Release SOP

Purpose
- Define steps to produce deterministic releases and safe rollouts.

Release flow
1. Ensure all PRs merged to `main` pass CI, security, performance, and docs checks.
2. Create a release branch `release/vX.Y.Z` and run full integration + e2e suites.
3. Build artifacts with pinned versions and upload to artifacts storage.
4. Deploy canary to staging with traffic shadowing for 1–2 hours.
5. Monitor SLOs; promote to production when canary metrics meet thresholds.

Rollback
- Maintain deployment scripts that accept a version tag. Rollback by redeploying previous tag and notifying stakeholders.

Ready
