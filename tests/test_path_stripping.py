import os
import sys
import tempfile
import shutil
import pytest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Source')))
from pypatch_url import command, patch


@pytest.fixture
def temp_module_with_nested_structure():
    """Create a temporary module with nested directory structure"""
    temp_dir = tempfile.mkdtemp()
    module_dir = os.path.join(temp_dir, 'testmodule')
    nested_dir = os.path.join(module_dir, 'subdir')
    os.makedirs(nested_dir)

    # Create a simple Python file in the nested directory
    with open(os.path.join(nested_dir, 'nested.py'), 'w') as f:
        f.write('def nested_function():\n    return "Nested function!"\n')

    yield temp_dir, module_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def nested_patch_file(temp_module_with_nested_structure):
    """Create a patch file that includes path components"""
    _, module_dir = temp_module_with_nested_structure
    patch_file = os.path.join(module_dir, 'nested.patch')

    with open(patch_file, 'w') as f:
        f.write('--- subdir/nested.py\t2023-01-01 12:00:00.000000000 -0000\n')
        f.write('+++ subdir/nested.py\t2023-01-01 12:01:00.000000000 -0000\n')
        f.write('@@ -1,2 +1,2 @@\n')
        f.write(' def nested_function():\n')
        f.write('-    return "Nested function!"\n')
        f.write('+    return "Patched nested function!"\n')

    return patch_file


def test_path_stripping(temp_module_with_nested_structure, nested_patch_file, monkeypatch):
    """Test path stripping functionality"""
    temp_dir, module_dir = temp_module_with_nested_structure

    # Mock sys.path to include our test module
    original_path = sys.path.copy()
    sys.path.insert(0, temp_dir)

    # Mock get_module_path to return our temp module path
    def mock_get_module_path(module_name):
        return module_dir

    monkeypatch.setattr(command, 'get_module_path', mock_get_module_path)

    # Create args mock with strip=1 to remove the first path component
    args = mock.Mock()
    args.module = 'testmodule'
    args.patch_file = nested_patch_file
    args.strip = 1

    # Apply the patch
    command.apply_patch(args, debug='ERROR')

    # Verify the file was patched
    with open(os.path.join(module_dir, 'subdir', 'nested.py'), 'r') as f:
        content = f.read()

    assert 'return "Patched nested function!"' in content

    # Restore sys.path
    sys.path = original_path
