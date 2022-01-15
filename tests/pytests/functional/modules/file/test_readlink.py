"""
Tests for file.readlink function
"""
# nox -e pytest-zeromq-3.8(coverage=False) -- -vvv --run-slow --run-destructive tests\pytests\functional\modules\file\test_readlink.py

import pytest
from salt.exceptions import SaltInvocationError

pytestmark = [
    pytest.mark.windows_whitelisted,
]


@pytest.fixture(scope="module")
def file(modules):
    return modules.file


@pytest.fixture(scope="function")
def source():
    with pytest.helpers.temp_file(contents="Source content") as source:
        yield source


def test_readlink(file, source):
    """
    Test readlink with defaults
    """
    target = source.parent / "symlink.lnk"
    target.symlink_to(source)
    try:
        result = file.readlink(path=target)
        assert result == str(source)
    finally:
        target.unlink()


def test_readlink_relative_path(file):
    """
    Test readlink with relative path
    Should throw a SaltInvocationError
    """
    with pytest.raises(SaltInvocationError) as exc:
        file.readlink(path="..\\test")
    assert "Path to link must be absolute" in exc.value.message


def test_readlink_not_a_link(file, source):
    """
    Test readlink where the path is not a link
    Should throw a SaltInvocationError
    """
    with pytest.raises(SaltInvocationError) as exc:
        file.readlink(path=source)
    assert "A valid link was not specified" in exc.value.message


def test_readlink_non_canonical(file, source):
    """
    Test readlink where there are nested symlinks and canonicalize=False
    Should resolve to the first symlink
    """
    intermediate = source.parent / "intermediate.lnk"
    intermediate.symlink_to(source)
    target = source.parent / "symlink.lnk"
    target.symlink_to(intermediate)
    try:
        result = file.readlink(path=target)
        assert result == str(intermediate)
    finally:
        intermediate.unlink()
        target.unlink()


def test_readlink_canonical(file, source):
    """
    Test readlink where there are nested symlinks and canonicalize=True
    Should resolve all nested symlinks returning the path to the source file
    """
    intermediate = source.parent / "intermediate.lnk"
    intermediate.symlink_to(source)
    target = source.parent / "symlink.lnk"
    target.symlink_to(intermediate)
    try:
        result = file.readlink(path=target, canonicalize=True)
        assert result == str(source)
    finally:
        intermediate.unlink()
        target.unlink()
