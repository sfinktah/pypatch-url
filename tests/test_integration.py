import os
import sys
import unittest.mock as mock
from pypatch_url import command




def test_url_with_path_stripping(deeper_nested_module, mock_url_response, mock_module_path, monkeypatch):
    """Test patch downloading from URL with path stripping"""
    temp_dir, module_dir = deeper_nested_module

    # Setup mock module path
    original_path = mock_module_path(temp_dir, module_dir)

    # Create mock patch content with nested paths
    patch_content = (
        '--- stripme/metoo/subdir/deeper/deep.py\t2023-01-01 12:00:00.000000000 -0000\n'
        '+++ stripme/metoo/subdir/deeper/deep.py\t2023-01-01 12:01:00.000000000 -0000\n'
        '@@ -1,2 +1,2 @@\n'
        ' def deep_function():\n'
        '-    return "Deep nested function!"\n'
        '+    return "Deep nested function patched from URL!"\n'
    )

    # Setup mock URL response
    mock_url_response(patch_content, monkeypatch)

    # Create args mock with a URL as patch_file and strip=1
    args = mock.Mock()
    args.module = 'testmodule'
    args.patch_file = 'https://example.com/patches/deep.patch'
    args.strip = 2

    # Apply the patch
    command.apply_patch(args, debug='ERROR')

    # Verify the file was patched
    with open(os.path.join(module_dir, 'subdir', 'deeper', 'deep.py'), 'r') as f:
        content = f.read()

    assert 'return "Deep nested function patched from URL!"' in content

    # Restore sys.path
    os.sys.path = original_path
