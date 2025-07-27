.PHONY: test test-cov clean

test:
	pytest

test-cov:
	pytest --cov=pypatch_url tests/

clean:
	rm -rf build/ dist/ *.egg-info/ .coverage .pytest_cache/ **/__pycache__/
