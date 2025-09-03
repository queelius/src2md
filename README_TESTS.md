# src2md Test Suite

## Overview

Comprehensive test suite for src2md v2.0 with the new fluent API and context window optimization.

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures and test utilities
├── unit/                 # Unit tests for individual components
│   ├── test_context.py   # Context window management tests
│   ├── test_importance.py # File importance scoring tests
│   ├── test_repository.py # Repository class tests
│   └── test_formatters.py # Output formatter tests
└── integration/          # Integration tests
    └── test_pipeline.py  # End-to-end pipeline tests
```

## Running Tests

### Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
make test
# or
pytest tests/
```

### Run Unit Tests Only
```bash
make test-unit
# or
pytest tests/unit/
```

### Run Integration Tests Only
```bash
make test-int
# or
pytest tests/integration/
```

### Run with Coverage
```bash
make coverage
# or
pytest --cov=src2md --cov-report=html tests/
```

### Run Specific Test
```bash
pytest tests/unit/test_context.py::TestContextWindow
```

## Test Coverage

The test suite covers:

### Unit Tests (78 tests)
- **Context Management** (13 tests)
  - ContextWindow enum values
  - TokenBudget allocation and consumption
  - TokenCounter with tiktoken
  - ContextOptimizer with various windows

- **Importance Scoring** (16 tests)
  - Weight normalization
  - File type detection (entrypoints, tests, configs)
  - Language-specific analysis (Python, JavaScript)
  - Complexity and documentation scoring
  - File ranking by importance

- **Repository Class** (16 tests)
  - Fluent API method chaining
  - File collection and filtering
  - Language detection
  - Context optimization
  - Multiple output formats

- **Formatters** (33 tests)
  - Base formatter interface
  - Markdown formatting
  - JSON/JSONL formatting
  - HTML formatting with escaping

### Integration Tests (12 tests)
- Complete pipeline with fluent API
- Context window optimization
- Multi-format output generation
- Importance-based prioritization
- Progressive summarization

## Key Test Features

### Fixtures
- `temp_dir`: Temporary directory for file operations
- `sample_repo`: Complete sample repository structure
- `sample_python_content`: Python code for testing
- `sample_javascript_content`: JavaScript code for testing

### Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.requires_tiktoken`: Tests requiring tiktoken

## Example Test

```python
def test_fluent_api_pipeline(sample_repo):
    """Test complete pipeline with fluent API."""
    result = (Repository(sample_repo)
        .name("TestProject")
        .branch("main")
        .with_importance_scoring()
        .optimize_for(ContextWindow.GPT_4)
        .analyze()
        .to_markdown())
    
    assert "# TestProject" in result
    assert "```python" in result
```

## Known Issues

- Some integration tests may timeout with very large repositories
- Tiktoken is required for accurate token counting tests
- File modification time tests depend on filesystem precision

## Contributing

When adding new features:
1. Write unit tests for individual components
2. Add integration tests for end-to-end workflows
3. Ensure all tests pass before committing
4. Maintain test coverage above 80%