from pathlib import Path

import fastgenomics.io as fg_io

HERE = Path(__file__).parent

dir_app = HERE / 'sample_app'
dir_data_1 = HERE / 'sample_data'
dir_data_2 = HERE / 'sample_data_2'


def test_change_path():
    fg_io.set_paths(dir_app, dir_data_1)
    assert fg_io.get_parameter('IntValue') == 150
    assert fg_io.get_parameter('StrValue') == 'hello from parameters.json'

    fg_io.set_paths(dir_app, dir_data_2)
    assert fg_io.get_parameter('StrValue') == 'hello from app 2’s parameters.json'
