"""Tests for `check_pip_compile` package."""

# Third party modules
import pytest

# First party modules
import check_pip_compile


def test_version():
    assert check_pip_compile.__version__.count(".") == 2


def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0
