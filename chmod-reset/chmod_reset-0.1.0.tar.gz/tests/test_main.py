# -*- coding: utf-8 -*-
import pytest
import os, sys
import stat

DIR_stats = (stat.S_IFDIR |
             stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
             stat.S_IRGRP | stat.S_IXGRP |
             stat.S_IROTH | stat.S_IXOTH)
FILE_stats = (stat.S_IRUSR | stat.S_IWUSR |
              stat.S_IRGRP | stat.S_IROTH)

from chmod_reset.__main__ import main

folder_name = 'tests/folder'
file_name = 'tests/folder/file'

os.chmod(file_name, 0)
os.chmod(folder_name, 0)

def test_main():
    main([folder_name])
    assert os.stat(folder_name).st_mode == DIR_stats
    assert stat.S_IMODE(os.stat(file_name).st_mode) == FILE_stats

def test_err():
    with pytest.raises(ValueError):
        main(['wrong'])
