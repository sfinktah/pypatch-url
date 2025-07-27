import os
import sys
import tempfile
import shutil
import pytest
from unittest import mock
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Source')))
from pypatch_url import command


@pytest.fixture
def temp_module():
    """Create a temporary module structure for testing"""
    temp_dir = tempfile.mkdtemp()
    module_dir = os.path.join(temp_dir, 'testmodule')
    os.makedirs(module_dir)

    # Create a simple Python file to be patched
    with open(os.path.join(module_dir, 'example.py'), 'w') as f:
        f.write('def hello_world():\n    return "Hello, World!"\n')

    yield temp_dir, module_dir

    # Cleanup
    shutil.rmtree(temp_dir)


def test_command_line_interface(temp_module, test_data_dir, monkeypatch):
    """Test the command line interface by mocking sys.argv"""
    temp_dir, module_dir = temp_module
    patch_file = os.path.join(test_data_dir, 'sample.patch')

    # Mock sys.path to include our test module
    original_path = sys.path.copy()
    sys.path.insert(0, temp_dir)

    # Mock get_module_path to return our temp module path
    def mock_get_module_path(module_name):
        return module_dir

    monkeypatch.setattr(command, 'get_module_path', mock_get_module_path)

    # Mock sys.argv
    with mock.patch('sys.argv', ['pypatch-url', 'apply', patch_file, 'testmodule']):
        # Mock sys.exit so the test doesn't actually exit
        with mock.patch('sys.exit'):
            command.main()

    # Verify the file was patched
    with open(os.path.join(module_dir, 'example.py'), 'r') as f:
        content = f.read()

    assert 'return "Hello, Patched World!"' in content

    # Restore sys.path
    sys.path = original_path


def test_command_with_strip_option(temp_module, test_data_dir, monkeypatch):
    """Test the command line interface with strip option"""
    temp_dir, module_dir = temp_module
    nested_dir = os.path.join(module_dir, 'subdir')
    os.makedirs(nested_dir, exist_ok=True)

    # Create a simple Python file in the nested directory
    with open(os.path.join(nested_dir, 'nested.py'), 'w') as f:
        f.write('def nested_function():\n    return "Nested function!"\n')

    patch_file = os.path.join(test_data_dir, 'nested_path.patch')

    # Mock sys.path to include our test module
    original_path = sys.path.copy()
    sys.path.insert(0, temp_dir)

    # Mock get_module_path to return our temp module path
    def mock_get_module_path(module_name):
        return module_dir

    monkeypatch.setattr(command, 'get_module_path', mock_get_module_path)

    # Mock sys.argv with -p 1 option
    with mock.patch('sys.argv', ['pypatch-url', 'apply', '-p', '1', patch_file, 'testmodule']):
        # Mock sys.exit so the test doesn't actually exit
        with mock.patch('sys.exit'):
            command.main()

    # Verify the file was patched
    with open(os.path.join(module_dir, 'subdir', 'nested.py'), 'r') as f:
        content = f.read()

    assert 'return "Patched nested function!"' in content

    # Restore sys.path
    sys.path = original_path
