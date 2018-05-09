from .context import zen
from zen.const import INDEX, STOCKS


def test_index():
    assert len(INDEX) == 26
