import os
import sys
import tempfile
import shutil
import pytest
from unittest import mock
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Source')))
from pypatch_url import command, patch


@pytest.fixture
def temp_module_with_nested_structure():
    """Create a temporary module with nested directory structure"""
    temp_dir = tempfile.mkdtemp()
    module_dir = os.path.join(temp_dir, 'testmodule')
    nested_dir = os.path.join(module_dir, 'subdir', 'deeper')
    os.makedirs(nested_dir)

    # Create a simple Python file in the deeply nested directory
    with open(os.path.join(nested_dir, 'deep.py'), 'w') as f:
        f.write('def deep_function():\n    return "Deep nested function!"\n')

    yield temp_dir, module_dir

    # Cleanup
    shutil.rmtree(temp_dir)


def test_url_with_path_stripping(temp_module_with_nested_structure, monkeypatch):
    """Test patch downloading from URL with path stripping"""
    temp_dir, module_dir = temp_module_with_nested_structure

    # Create mock patch content with nested paths
    patch_content = (
        '--- subdir/deeper/deep.py\t2023-01-01 12:00:00.000000000 -0000\n'
        '+++ subdir/deeper/deep.py\t2023-01-01 12:01:00.000000000 -0000\n'
        '@@ -1,2 +1,2 @@\n'
        ' def deep_function():\n'
        '-    return "Deep nested function!"\n'
        '+    return "Deep nested function patched from URL!"\n'
    )

    # Mock the urlopen function to return our patch content
    def mock_urlopen(url):
        return StringIO(patch_content)

    monkeypatch.setattr('six.moves.urllib.request.urlopen', mock_urlopen)

    # Mock sys.path to include our test module
    original_path = sys.path.copy()
    sys.path.insert(0, temp_dir)

    # Mock get_module_path to return our temp module path
    def mock_get_module_path(module_name):
        return module_dir

    monkeypatch.setattr(command, 'get_module_path', mock_get_module_path)

    # Create args mock with a URL as patch_file and strip=1
    args = mock.Mock()
    args.module = 'testmodule'
    args.patch_file = 'https://example.com/patches/deep.patch'
    args.strip = 1

    # Apply the patch
    command.apply_patch(args, debug='ERROR')

    # Verify the file was patched
    with open(os.path.join(module_dir, 'subdir', 'deeper', 'deep.py'), 'r') as f:
        content = f.read()

    assert 'return "Deep nested function patched from URL!"' in content

    # Restore sys.path
    sys.path = original_path
