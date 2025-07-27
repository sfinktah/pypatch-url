import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Source')))
from pypatch_url import patch


def test_path_strip_function():
    """Test the pathstrip utility function"""
    # Test stripping one level
    assert patch.pathstrip('dir1/dir2/file.py', 1) == 'dir2/file.py'

    # Test stripping multiple levels
    assert patch.pathstrip('dir1/dir2/dir3/file.py', 2) == 'dir3/file.py'

    # Test stripping all levels
    assert patch.pathstrip('dir1/dir2/file.py', 2) == 'file.py'

    # Test with Windows path separators
    assert patch.pathstrip('dir1\\dir2\\file.py', 1) == 'dir2/file.py'


def test_xnormpath_function():
    """Test the cross-platform path normalization function"""
    # Test normalization
    assert patch.xnormpath('dir1/./dir2/../dir3/file.py') == 'dir1/dir3/file.py'

    # Test with Windows path separators
    if os.name == 'nt':  # Only run on Windows
        assert patch.xnormpath('dir1\\dir2\\file.py') == 'dir1/dir2/file.py'


def test_xstrip_function():
    """Test the path stripping security function"""
    # Test absolute Unix path
    assert patch.xstrip('/dir1/dir2/file.py') == 'dir1/dir2/file.py'

    # Test absolute Windows path
    assert patch.xstrip('C:/dir1/dir2/file.py') == 'dir1/dir2/file.py'
    assert patch.xstrip('C:\\dir1\\dir2\\file.py') == 'dir1/dir2/file.py'

    # Test relative path (should remain unchanged)
    assert patch.xstrip('dir1/dir2/file.py') == 'dir1/dir2/file.py'
