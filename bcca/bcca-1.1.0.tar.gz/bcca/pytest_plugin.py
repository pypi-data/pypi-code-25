from _pytest.assertion.util import assertrepr_compare
from io import StringIO
from unittest import mock


class FakeStringIO(StringIO):
    def __eq__(self, other):
        if isinstance(other, str):
            return self.getvalue() == other.strip()
        else:
            return super().__eq__(other)

    def __repr__(self):
        return repr(self.getvalue())


def pytest_assertrepr_compare(config, op, left, right):
    if isinstance(left, FakeStringIO) and isinstance(right, str) and op == '==':
        return assertrepr_compare(config, op, left.getvalue(), right)
