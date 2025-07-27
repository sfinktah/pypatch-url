import os
import sys
import tempfile
import shutil
import pytest
# First we need to adjust the path to find the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import the test dependencies
import unittest.mock as mock
from io import StringIO

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
        f.write('def url_function():\n    return "Original function"\n')

    yield temp_dir, module_dir

    # Cleanup with error handling for Windows permission issues
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        pass


def test_url_download(temp_module, monkeypatch):
    """Test patch downloading from URL"""
    # Get the temporary module directories from the fixture
    temp_dir, module_dir = temp_module

    # Create mock patch content
    patch_content = (
        '--- example.py\t2023-01-01 12:00:00.000000000 -0000\n'
        '+++ example.py\t2023-01-01 12:01:00.000000000 -0000\n'
        '@@ -1,2 +1,2 @@\n'
        ' def url_function():\n'
        '-    return "Original function"\n'
        '+    return "Function patched from URL"\n'
    )

    # Mock the urlopen function to return our patch content
    def mock_urlopen(url):
        return StringIO(patch_content)

    # In pytest, we can directly monkeypatch the module
    # This will properly handle cleanup automatically
    monkeypatch.setattr('six.moves.urllib.request.urlopen', mock_urlopen)

    # Mock sys.path to include our test module
    original_path = sys.path.copy()
    sys.path.insert(0, temp_dir)

    # Mock get_module_path to return our temp module path
    def mock_get_module_path(module_name):
        return module_dir

    monkeypatch.setattr(command, 'get_module_path', mock_get_module_path)

    # Create args mock with a URL as patch_file
    args = mock.Mock()
    args.module = 'testmodule'
    args.patch_file = 'https://example.com/patches/example.patch'
    args.strip = None

    # Apply the patch
    result = command.apply_patch(args, debug=False)
    assert result, "Patch application failed"

    # Verify the file was patched
    with open(os.path.join(module_dir, 'example.py'), 'r') as f:
        content = f.read()

    assert 'return "Function patched from URL"' in content, "Patch was not applied correctly"

    # Restore sys.path
    sys.path = original_path
