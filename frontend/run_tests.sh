#!/bin/bash

# Frontend Test Runner Script
# Run all tests with coverage for the News Analytics Platform frontend

echo "===================================="
echo "News Analytics Frontend - Test Suite"
echo "===================================="
echo ""

# Change to frontend directory
cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo ""
fi

echo "===================================="
echo "Running Test Suite"
echo "===================================="
echo ""

# Run tests with coverage
npm run test:coverage

TEST_EXIT_CODE=$?

echo ""
echo "===================================="
echo "Coverage Report"
echo "===================================="
echo ""
echo "HTML coverage report generated at: coverage/index.html"
echo ""

# Exit with test result code
exit $TEST_EXIT_CODE
