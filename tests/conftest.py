# This file contains shared pytest fixtures and configurations
import os
import sys
import tempfile
import shutil
import pytest
import unittest.mock as mock
from io import StringIO

# Import our package modules
from pypatch_url import command
from pypatch_url import patch

# Ensure our package can be imported by adding the source directory to sys.path
python_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if python_path not in sys.path:
    sys.path.insert(0, python_path)


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to the test data directory"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


def create_temp_module_structure(structure_def):
    """Helper function to create a temporary module structure

    Args:
        structure_def: Dictionary with keys as relative paths and values as file content

    Returns:
        Tuple of (temp_dir, module_dir)
    """
    temp_dir = tempfile.mkdtemp()
    module_dir = os.path.join(temp_dir, 'testmodule')

    # Create all directories and files defined in structure_def
    for rel_path, content in structure_def.items():
        # Calculate the full path
        full_path = os.path.join(module_dir, rel_path)

        # Ensure the directory exists
        dir_path = os.path.dirname(full_path)
        os.makedirs(dir_path, exist_ok=True)

        # Write the file content
        with open(full_path, 'w') as f:
            f.write(content)

    return temp_dir, module_dir


def cleanup_temp_dir(temp_dir):
    """Helper function to clean up temporary directory with error handling"""
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        # print(f"Warning: Could not remove temporary directory {temp_dir} - it may be in use")
        pass


@pytest.fixture
def temp_module():
    """Create a temporary module structure for testing"""
    structure = {
        'example.py': 'def hello_world():\n    return "Hello, World!"\n'
    }

    temp_dir, module_dir = create_temp_module_structure(structure)
    yield temp_dir, module_dir
    cleanup_temp_dir(temp_dir)


@pytest.fixture
def temp_module_with_nested_structure():
    """Create a temporary module with nested directory structure"""
    structure = {
        'subdir/nested.py': 'def nested_function():\n    return "Nested function!"\n'
    }

    temp_dir, module_dir = create_temp_module_structure(structure)
    yield temp_dir, module_dir
    cleanup_temp_dir(temp_dir)


@pytest.fixture
def deeper_nested_module():
    """Create a temporary module with deeper nested directory structure"""
    structure = {
        'subdir/deeper/deep.py': 'def deep_function():\n    return "Deep nested function!"\n'
    }

    temp_dir, module_dir = create_temp_module_structure(structure)
    yield temp_dir, module_dir
    cleanup_temp_dir(temp_dir)


@pytest.fixture
def mock_module_path(monkeypatch):
    """Fixture to mock module path for testing"""
    def setup_mock(temp_dir, module_dir):
        # Mock sys.path to include our test module
        original_path = sys.path.copy()
        sys.path.insert(0, temp_dir)

        # Mock get_module_path to return our temp module path
        def mock_get_module_path(module_name):
            return module_dir

        monkeypatch.setattr(command, 'get_module_path', mock_get_module_path)

        return original_path

    return setup_mock


class MockResponse:
    """Mock response class for URL mocking"""
    def __init__(self, content):
        if isinstance(content, str):
            self.content = content.encode('utf-8')
        else:
            self.content = content

    def read(self):
        return self.content


@pytest.fixture
def mock_url_response():
    """Create a mock URL response for testing"""

    def create_mock(patch_content, monkeypatch):
        # Mock the urlopen function to return our patch content
        def mock_urlopen(url):
            # Verify the URL is valid to avoid real HTTP requests in tests
            if not url or not isinstance(url, str):
                raise ValueError("Invalid URL provided")
            # Return a mock response object that simulates a URL response
            return MockResponse(patch_content)

        # Use pytest's monkeypatch which correctly handles the complexities of six.moves
        monkeypatch.setattr('six.moves.urllib.request.urlopen', mock_urlopen)

    return create_mock