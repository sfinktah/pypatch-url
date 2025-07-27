import os
import sys
import tempfile
import shutil
import pytest

# First we need to adjust the path to find the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import the test dependencies
import unittest.mock as mock

# Import our package modules
from pypatch_url import command
from pypatch_url import patch


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

    # Cleanup with error handling for Windows permission issues
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except PermissionError:
        pass


@pytest.fixture
def simple_patch_file(temp_module):
    """Create a simple patch file"""
    _, module_dir = temp_module
    patch_file = os.path.join(module_dir, 'example.patch')

    with open(patch_file, 'w') as f:
        f.write('--- example.py\t2023-01-01 12:00:00.000000000 -0000\n')
        f.write('+++ example.py\t2023-01-01 12:01:00.000000000 -0000\n')
        f.write('@@ -1,2 +1,2 @@\n')
        f.write(' def hello_world():\n')
        f.write('-    return "Hello, World!"\n')
        f.write('+    return "Hello, Patched World!"\n')

    return patch_file


def test_basic_functionality(temp_module, simple_patch_file, monkeypatch):
    """Test basic patch application functionality"""
    temp_dir, module_dir = temp_module

    # Mock sys.path to include our test module
    original_path = sys.path.copy()
    sys.path.insert(0, temp_dir)

    # Mock get_module_path to return our temp module path
    def mock_get_module_path(module_name):
        return module_dir

    monkeypatch.setattr(command, 'get_module_path', mock_get_module_path)

    # Create args mock
    args = mock.Mock()
    args.module = 'testmodule'
    args.patch_file = simple_patch_file
    args.strip = None

    # Apply the patch
    command.apply_patch(args, debug='ERROR')

    # Verify the file was patched
    with open(os.path.join(module_dir, 'example.py'), 'r') as f:
        content = f.read()

    assert 'return "Hello, Patched World!"' in content

    # Restore sys.path
    sys.path = original_path
