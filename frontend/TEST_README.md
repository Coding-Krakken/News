# Frontend Test Suite Documentation

## Overview

Comprehensive test suite for the News Analytics Platform frontend with 80%+ code coverage.

## Test Structure

```
src/
├── __tests__/
│   ├── App.test.jsx                    # Main app component tests
│   ├── components/
│   │   ├── Filters.test.jsx           # Filter component tests
│   │   ├── StoryCard.test.jsx         # Story card tests
│   │   └── StoryDetail.test.jsx       # Story detail tests
│   ├── pages/
│   │   ├── StoriesPage.test.jsx       # Stories page tests
│   │   └── AnalyticsPage.test.jsx     # Analytics page tests
│   └── services/
│       └── api.test.js                 # API service tests
└── test/
    ├── setup.js                        # Test setup and configuration
    └── utils.jsx                       # Test utilities and mock data
```

## Test Categories

### Component Tests
- **App.jsx**: Navigation, page switching, header
- **StoryCard**: Rendering, user interactions, data display
- **StoryDetail**: Story display, fact ledger, coverage matrix
- **Filters**: Facet loading, filter selection, state management

### Page Tests
- **StoriesPage**: Story list, actions (ingest, cluster), navigation
- **AnalyticsPage**: Statistics display, data visualization

### Service Tests
- **API Services**: All API calls, error handling, data formatting

## Running Tests

### Quick Start

```bash
cd frontend
./run_tests.sh
```

### Manual Execution

```bash
cd frontend
npm install
npm test
```

### Run with Coverage

```bash
npm run test:coverage
```

### Run in Watch Mode

```bash
npm test
```

### Run with UI

```bash
npm run test:ui
```

## Test Infrastructure

### Testing Libraries
- **Vitest**: Fast test runner compatible with Vite
- **@testing-library/react**: Component testing utilities
- **@testing-library/jest-dom**: Custom matchers
- **@testing-library/user-event**: User interaction simulation
- **MSW**: API mocking (for integration tests)

### Configuration Files
- `vite.config.js`: Vitest configuration with coverage settings
- `src/test/setup.js`: Global test setup
- `src/test/utils.jsx`: Shared test utilities and mock data

## Coverage Targets

- **Lines**: 80%
- **Functions**: 80%
- **Branches**: 80%
- **Statements**: 80%

## Test Statistics

- **Total Test Files**: 7
- **Total Test Functions**: 70+
- **Component Tests**: 40+
- **Service Tests**: 15+
- **Integration Tests**: 15+

## What's Tested

### Components
✅ User interactions (clicks, form submissions)
✅ Conditional rendering
✅ Props validation
✅ State management
✅ Error handling
✅ Loading states

### Services
✅ API calls
✅ Request parameters
✅ Response handling
✅ Error handling

### Pages
✅ Page navigation
✅ Data fetching
✅ User workflows
✅ State management

## Mock Data

Mock data is centralized in `src/test/utils.jsx`:
- Sample stories
- Sample articles
- Sample statistics
- Sample fact ledgers
- Sample coverage data

## Best Practices

1. **Use descriptive test names**: Test names should clearly describe what is being tested
2. **Test user behavior**: Focus on testing what users see and do
3. **Avoid implementation details**: Don't test internal state or methods
4. **Use proper queries**: Prefer `getByRole`, `getByLabelText` over `getByTestId`
5. **Clean up**: Use `cleanup()` after each test (automatic with setup)
6. **Mock external dependencies**: API calls, timers, etc.

## Adding New Tests

### Component Test Template

```javascript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import MyComponent from '../MyComponent'

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('should handle user interaction', () => {
    const mockFn = vi.fn()
    render(<MyComponent onClick={mockFn} />)
    fireEvent.click(screen.getByRole('button'))
    expect(mockFn).toHaveBeenCalled()
  })
})
```

### Service Test Template

```javascript
import { describe, it, expect, vi } from 'vitest'
import axios from 'axios'
import { myService } from '../services/api'

vi.mock('axios')

describe('myService', () => {
  it('should call API correctly', async () => {
    axios.get.mockResolvedValue({ data: { result: 'success' } })
    const result = await myService.getData()
    expect(axios.get).toHaveBeenCalledWith('/api/endpoint')
    expect(result).toEqual({ result: 'success' })
  })
})
```

## Debugging Tests

### View Test UI

```bash
npm run test:ui
```

This opens a browser interface showing:
- Test results
- Code coverage
- Failed tests with details

### Debug Single Test

```bash
npm test -- MyComponent.test
```

### Check Coverage

```bash
npm run test:coverage
open coverage/index.html
```

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Frontend Tests
  run: |
    cd frontend
    npm ci
    npm run test:coverage
```

## Troubleshooting

### Tests Failing Locally

1. Clear node_modules: `rm -rf node_modules && npm install`
2. Clear Vitest cache: `npx vitest --clearCache`
3. Check Node version: `node --version` (requires 18+)

### Coverage Not Meeting Threshold

1. Identify uncovered lines: Check `coverage/index.html`
2. Add missing tests for uncovered code
3. Consider if code can be refactored to be more testable

## Future Enhancements

- E2E tests with Playwright
- Visual regression tests
- Performance tests
- Accessibility tests (a11y)
- Snapshot tests for UI components
