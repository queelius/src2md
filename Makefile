.PHONY: help install install-dev test test-unit test-integration coverage clean lint format

help:
	@echo "Available commands:"
	@echo "  install       Install dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  test         Run all tests"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-int     Run integration tests only"
	@echo "  coverage     Run tests with coverage report"
	@echo "  clean        Remove build artifacts and cache"
	@echo "  lint         Run code linting"
	@echo "  format       Format code with black"

install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-test.txt
	pip install -e .

test:
	pytest -v tests/

test-unit:
	pytest -v tests/unit/

test-int:
	pytest -v tests/integration/

coverage:
	pytest --cov=src2md --cov-report=term-missing --cov-report=html tests/
	@echo "Coverage report generated in htmlcov/index.html"

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf build dist *.egg-info

lint:
	ruff check src2md/
	mypy src2md/ --ignore-missing-imports

format:
	black src2md/ tests/