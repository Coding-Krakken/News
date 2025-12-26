#!/bin/bash

# Test runner script for News Analytics Platform
# This script runs all tests and generates coverage reports

echo "===================================="
echo "News Analytics Platform - Test Suite"
echo "===================================="
echo ""

# Change to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
# Fast test path: install a trimmed set of packages to avoid long installs
if [ "$FAST_TEST" = "1" ]; then
    echo "FAST_TEST=1 detected — installing test-only requirements..."
    pip install -q -r requirements-test.txt
else
    pip install -q -r requirements.txt
fi

echo ""
echo "===================================="
echo "Running Test Suite"
echo "===================================="
echo ""

# Run tests with coverage
pytest -v \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    --cov-fail-under=95 \
    "$@"

TEST_EXIT_CODE=$?

echo ""
echo "===================================="
echo "Coverage Report"
echo "===================================="
echo ""

# Display coverage summary
if [ -f ".coverage" ]; then
    coverage report
fi

echo ""
echo "HTML coverage report generated at: htmlcov/index.html"
echo ""

# Exit with test result code
exit $TEST_EXIT_CODE
