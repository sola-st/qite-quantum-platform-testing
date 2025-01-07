import pytest
from information_distillation.get_changelogs import get_version_from_file


def test_get_version_from_file_valid_version():
    """Test that a valid version is correctly extracted from the file path."""
    file_path = 'releasenotes/notes/0.18/add-alignment-management-passes-650b8172e1426a73.yaml'
    assert get_version_from_file(file_path) == '0.18'


def test_get_version_from_file_invalid_version():
    """Test that an invalid version returns None."""
    file_path = 'releasenotes/notes/invalid_version/add-alignment-management-passes-650b8172e1426a73.yaml'
    assert get_version_from_file(file_path) is None


def test_get_version_from_file_no_version():
    """Test that a file path without a version returns None."""
    file_path = 'releasenotes/notes/add-alignment-management-passes-650b8172e1426a73.yaml'
    assert get_version_from_file(file_path) is None


def test_get_version_from_file_malformed_version():
    """Test that a malformed version returns None."""
    file_path = 'releasenotes/notes/0.18a/add-alignment-management-passes-650b8172e1426a73.yaml'
    assert get_version_from_file(file_path) is None
