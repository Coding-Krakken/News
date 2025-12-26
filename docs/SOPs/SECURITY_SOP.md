Security SOP

Purpose

- Standardize security reviews, scans, and incident handling.

Pre-merge checks

- Run dependency scans (`safety` for Python, `npm audit` for Node).
- Run static analysis (`bandit` for Python) and secret scans (`git-secrets`).
- Verify no secrets in code and environment variables are documented.

Incident handling

1. Triage severity (critical/high/medium/low).
2. If critical: create incident channel, notify on-call, and block merges until fix.
3. Run forensics and publish a brief postmortem with timelines.

Ready
