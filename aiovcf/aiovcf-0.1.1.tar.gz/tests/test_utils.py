import pytest

from aiovcf.utils import fbool, fint, to_typed_value


def test_to_typed_value():
    assert to_typed_value("5", int) == 5
    assert to_typed_value("5.0", fint) == pytest.approx(5.0)
    assert to_typed_value("xxy", int) is None
    assert to_typed_value("xxy", fint) is None


def test_fint():
    assert fint(None) is None
    assert fint("5x") is None
    assert fint("x5") is None
    assert fint("3.14159") == pytest.approx(3.14159)
    assert fint("3") == 3


def test_fbool():
    assert fbool(False) is False
    assert fbool(None) is False
    assert fbool(0) is False
    assert fbool(0.0) is False
    assert fbool("0") is False
    assert fbool("0.0") is False
    assert fbool("") is False

    assert fbool(True) is True
    assert fbool(1) is True
    assert fbool(-1) is True
    assert fbool(1.0) is True
    assert fbool(-1.0) is True
    assert fbool("1.0") is True
    assert fbool("abc") is True

    # odd balls (not doing literal eval...)
    assert fbool("None") is True
    assert fbool("False") is True
    assert fbool("True") is True
