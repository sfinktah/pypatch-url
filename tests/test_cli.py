import os
import unittest.mock as mock
from pypatch_url import command


def test_command_line_interface(temp_module, test_data_dir, mock_module_path, monkeypatch):
    """Test the command line interface by mocking sys.argv"""
    temp_dir, module_dir = temp_module
    patch_file = os.path.join(test_data_dir, 'sample.patch')

    # Setup mock module path
    original_path = mock_module_path(temp_dir, module_dir)

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
    os.sys.path = original_path


def test_command_with_strip_option(temp_module_with_nested_structure, test_data_dir, mock_module_path, monkeypatch):
    """Test the command line interface with strip option"""
    temp_dir, module_dir = temp_module_with_nested_structure
    patch_file = os.path.join(test_data_dir, 'nested_path.patch')

    # Setup mock module path
    original_path = mock_module_path(temp_dir, module_dir)

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
    os.sys.path = original_path
