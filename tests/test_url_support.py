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
def temp_module():
    """Create a temporary module structure for testing"""
    temp_dir = tempfile.mkdtemp()
    module_dir = os.path.join(temp_dir, 'testmodule')
    os.makedirs(module_dir)

    # Create a simple Python file to be patched
    with open(os.path.join(module_dir, 'example.py'), 'w') as f:
        f.write('def url_function():\n    return "Original function"\n')

    yield temp_dir, module_dir

    # Cleanup
    shutil.rmtree(temp_dir)


def test_url_download(temp_module, monkeypatch):
    """Test patch downloading from URL"""
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
    command.apply_patch(args, debug='ERROR')

    # Verify the file was patched
    with open(os.path.join(module_dir, 'example.py'), 'r') as f:
        content = f.read()

    assert 'return "Function patched from URL"' in content

    # Restore sys.path
    sys.path = original_path
