#!/usr/bin/env bash
set -euo pipefail

echo "Running docs smoke checks..."

# Run markdownlint (installed globally in CI) if available
if command -v markdownlint >/dev/null 2>&1; then
  echo "markdownlint found — running on docs/"
  markdownlint "docs/**/*.md" || true
else
  echo "markdownlint not installed; skipping markdown lint"
fi

# Run simple doc examples validation (search for example commands and attempt no-op)
echo "Validating runnable examples: (no-op)"
grep -R "curl" docs || true

echo "Docs smoke checks complete"
