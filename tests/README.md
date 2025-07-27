# pypatch-url Tests

This directory contains test cases for the pypatch-url utility.

## Test Structure

- `test_basic.py`: Tests basic functionality of applying patches
- `test_path_stripping.py`: Tests the path stripping functionality with `-p` option
- `test_url_support.py`: Tests applying patches from URLs
- `test_cli.py`: Tests the command-line interface
- `test_integration.py`: Integration tests that combine multiple features
- `test_helpers.py`: Tests for utility functions

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_basic.py
```

To run a specific test:

```bash
pytest tests/test_basic.py::test_basic_functionality
```

## Test Data

The `data/` directory contains sample patch files used by the tests.
