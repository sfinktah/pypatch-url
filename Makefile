.PHONY: test test-basic test-cov clean install-dev
.PHONY: clean test test-cov lint format install install-dev

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=pypatch_url --cov-report=term-missing tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
install-dev:
	pip install -e ".[dev]"

test: install-dev
	pytest

test-basic:
	pypatch-url-test

test-cov: install-dev
	pytest --cov=pypatch_url tests/

clean:
	rm -rf build/ dist/ *.egg-info/ .coverage .pytest_cache/ **/__pycache__/
.PHONY: clean test test-cov build install

all: clean test build

clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/ .coverage htmlcov/

test:
	pytest

test-cov:
	pytest --cov=pypatch_url tests/

build: clean
	python -m build

install: build
	pip install -e .

install-dev: build
	pip install -e ".[dev]"