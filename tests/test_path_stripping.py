import os
import unittest.mock as mock
import pytest
from pypatch_url import command


@pytest.fixture
def nested_patch_file(temp_module_with_nested_structure):
    """Create a patch file that includes path components"""
    _, module_dir = temp_module_with_nested_structure
    patch_file = os.path.join(module_dir, 'nested.patch')

    with open(patch_file, 'w') as f:
        f.write('--- stripme/subdir/nested.py\t2023-01-01 12:00:00.000000000 -0000\n')
        f.write('+++ stripme/subdir/nested.py\t2023-01-01 12:01:00.000000000 -0000\n')
        f.write('@@ -1,2 +1,2 @@\n')
        f.write(' def nested_function():\n')
        f.write('-    return "Nested function!"\n')
        f.write('+    return "Patched nested function!"\n')

    return patch_file


def test_path_stripping(temp_module_with_nested_structure, nested_patch_file, mock_module_path, monkeypatch):
    """Test path stripping functionality"""
    temp_dir, module_dir = temp_module_with_nested_structure

    # Setup mock module path
    original_path = mock_module_path(temp_dir, module_dir)

    # Create args mock with strip=1 to remove the first path component
    args = mock.Mock()
    args.module = 'testmodule'
    args.patch_file = nested_patch_file
    args.strip = 1

    # Apply the patch
    result = command.apply_patch(args, debug='DEBUG')

    # Check that the patch was applied successfully
    assert result is True, "Patch application should succeed"

    # Verify the file was patched
    with open(os.path.join(module_dir, 'subdir', 'nested.py'), 'r') as f:
        content = f.read()

    assert 'return "Patched nested function!"' in content

    # Restore sys.path
    os.sys.path = original_path
