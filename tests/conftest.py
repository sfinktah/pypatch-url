# This file contains shared pytest fixtures and configurations
import pytest
import os

@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to the test data directory"""
    return os.path.join(os.path.dirname(__file__), 'data')
