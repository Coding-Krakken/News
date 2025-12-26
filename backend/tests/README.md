# Test Suite Documentation

## Overview

This comprehensive test suite provides 95%+ code coverage for the News Analytics Platform backend. It includes unit tests, integration tests, and end-to-end tests.

## Test Structure

```
tests/
├── conftest.py                          # Shared fixtures and configuration
├── test_main.py                         # Main application tests
├── unit/                                # Unit tests (isolated component testing)
│   ├── models/
│   │   └── test_schemas.py             # Data model validation tests
│   ├── services/
│   │   ├── test_ingestion.py           # News ingestion service tests
│   │   ├── test_clustering.py          # Story clustering service tests
│   │   ├── test_fact_checker.py        # Fact-checking service tests
│   │   └── test_analytics.py           # Analytics service tests
│   └── routes/                          # (Future API route unit tests)
├── integration/                         # Integration tests (API endpoints)
│   ├── test_articles_api.py            # Articles API integration tests
│   ├── test_stories_api.py             # Stories API integration tests
│   ├── test_analytics_api.py           # Analytics API integration tests
│   └── test_fact_checker_api.py        # Fact-checker API integration tests
└── e2e/                                 # End-to-end tests (complete workflows)
    └── test_complete_workflow.py       # Complete workflow tests
```

## Test Categories

### Unit Tests (`tests/unit/`)

- **Purpose**: Test individual components in isolation
- **Mocking**: External dependencies are mocked
- **Coverage**: Models, services, utilities
- **Examples**:
  - Data model validation
  - Service method logic
  - Business rule enforcement

### Integration Tests (`tests/integration/`)

- **Purpose**: Test API endpoints with database
- **Mocking**: Uses mock database (mongomock-motor)
- **Coverage**: API routes, request/response handling
- **Examples**:
  - REST API endpoints
  - Database operations
  - Request validation

### End-to-End Tests (`tests/e2e/`)

- **Purpose**: Test complete user workflows
- **Mocking**: Minimal mocking, full system integration
- **Coverage**: Multi-step processes
- **Examples**:
  - Article ingestion → clustering → analytics
  - Story creation → fact-checking
  - Coverage matrix generation

## Running Tests

### Quick Start

```bash
cd backend
./run_tests.sh
```

### Manual Execution

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
pytest
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run only e2e tests
pytest tests/e2e/ -v

# Run tests with specific marker
pytest -m unit -v
pytest -m integration -v
pytest -m e2e -v
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Test File

```bash
pytest tests/unit/services/test_ingestion.py -v
```

### Run Specific Test Function

```bash
pytest tests/unit/models/test_schemas.py::TestArticleModel::test_article_creation_with_valid_data -v
```

## Coverage Requirements

The test suite is configured to require **95% code coverage**. This is enforced in `pytest.ini`:

```ini
--cov-fail-under=95
```

### View Coverage Report

After running tests:

```bash
# View in terminal
coverage report

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `mock_db`: Mock MongoDB database
- `client`: Async HTTP client for API testing
- `sample_article_data`: Sample article data
- `sample_articles_list`: List of sample articles
- `sample_story_data`: Sample story data
- `sample_claim`: Sample claim data
- `mock_rss_feed`: Mock RSS feed XML
- `mock_openai_response`: Mock OpenAI API response

## Writing New Tests

### Unit Test Example

```python
import pytest
from app.services.ingestion import NewsIngestionService

class TestNewsIngestionService:
    @pytest.fixture
    def service(self):
        return NewsIngestionService()

    def test_add_source(self, service):
        initial_count = len(service.sources)
        service.add_source("Test", "url", "rss", "center", "US")
        assert len(service.sources) == initial_count + 1
```

### Integration Test Example

```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
class TestArticlesAPI:
    @pytest.mark.asyncio
    async def test_get_articles(self, client: AsyncClient):
        response = await client.get("/api/articles/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

### E2E Test Example

```python
import pytest
from httpx import AsyncClient

@pytest.mark.e2e
class TestWorkflow:
    @pytest.mark.asyncio
    async def test_complete_workflow(self, client: AsyncClient, mock_db):
        # Insert articles
        # Cluster stories
        # Get analytics
        # Generate fact ledger
        # Assert complete workflow
```

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -v
    --cov=app
    --cov-report=html
    --cov-fail-under=95
```

### Markers

Tests can be marked with:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests

## Mocking Strategy

### External Services

- **RSS Feeds**: Mocked with sample XML
- **OpenAI API**: Mocked responses
- **MongoDB**: mongomock-motor for async mocking
- **HTTP Requests**: aiohttp mocked with AsyncMock

### Example Mocking

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_with_mock(service):
    with patch('module.function', new_callable=AsyncMock) as mock_func:
        mock_func.return_value = "mocked result"
        result = await service.call_function()
        assert result == "mocked result"
```

## Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd backend
    pip install -r requirements.txt
    pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
```

## Test Data

### Sample Data Locations

- Article data: `conftest.py` → `sample_article_data`
- Story data: `conftest.py` → `sample_story_data`
- RSS feeds: `conftest.py` → `mock_rss_feed`

### Creating Test Data

```python
@pytest.fixture
def my_test_data():
    return {
        "field1": "value1",
        "field2": "value2"
    }
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with import errors

```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: Async tests hang

```bash
# Solution: Check asyncio_mode in pytest.ini
asyncio_mode = auto
```

**Issue**: Coverage below 95%

```bash
# Solution: Run coverage report to find gaps
pytest --cov=app --cov-report=term-missing
```

**Issue**: MongoDB connection errors

```bash
# Solution: Tests use mongomock, no real MongoDB needed
# Check conftest.py for proper mock setup
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Coverage**: Aim for edge cases and error conditions
4. **Speed**: Keep unit tests fast, use mocks
5. **Maintainability**: Use fixtures for common setup
6. **Documentation**: Comment complex test scenarios

## Test Metrics

Expected test metrics:

- **Total Tests**: 100+
- **Code Coverage**: ≥95%
- **Test Execution Time**: <30 seconds
- **Test Categories**: Unit (70%), Integration (20%), E2E (10%)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure 95%+ coverage for new code
3. Add integration tests for new endpoints
4. Update this documentation if needed

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [mongomock-motor](https://github.com/michaelkryukov/mongomock_motor)
