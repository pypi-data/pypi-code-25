import os
import pytest
from .context import zen
from zen import const

def test_loca_file_exists():
    assert os.path.exists(const.DAY_IX)
    # assert os.path.exists(const.MINUTE_IX)
    assert os.path.exists(const.DAY)
    # assert os.path.exists(const.MINUTE)
