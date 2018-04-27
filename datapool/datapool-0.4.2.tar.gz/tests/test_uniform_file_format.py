# encoding: utf-8
from __future__ import print_function, division, absolute_import

import shutil

import pytest
from datapool.uniform_file_format import read_from_file, read_from_string, check_rows, to_signals

from .conftest import not_for_root


def test_reader(regtest, data_path):
    rows = read_from_file(data_path("uniform_file.csv"))
    assert len(rows) == 2
    errors = check_rows(rows)
    assert not errors
    signals = to_signals(rows)

    for signal in signals:
        print(sorted(signal.items()), file=regtest)

    data = open(data_path("uniform_file.csv"), "r", encoding="ascii").read()
    rows = read_from_string(data)
    errors = check_rows(rows)
    assert not errors
    signals2 = to_signals(rows)

    assert signals == signals2

    with pytest.raises(ValueError):
        read_from_file(data_path("non_existent_uniform_file.csv"))


@not_for_root
def test_reader_wrong_permissions(tmpdir, data_path):
    new_path = tmpdir.join("file.csv")
    shutil.copyfile(data_path("uniform_file.csv"), new_path.strpath)
    new_path.chmod(0o000)

    with pytest.raises(IOError):
        read_from_file(data_path(new_path.strpath))


def test_wrong_header(data_path):
    with pytest.raises(ValueError):
        read_from_file(data_path("invalid_header_uniform_file.csv"))

    with pytest.raises(ValueError):
        read_from_file(data_path("invalid_header_uniform_file2.csv"))


def test_invalid_data_with_site(regtest, data_path):
    rows = read_from_file(data_path("invalid_data_uniform_file_site.csv"))
    for msg in check_rows(rows):
        print(msg, file=regtest)


def test_invalid_data_with_xyz(regtest, data_path):
    rows = read_from_file(data_path("invalid_data_uniform_file_xyz.csv"))
    for msg in check_rows(rows):
        print(msg, file=regtest)
