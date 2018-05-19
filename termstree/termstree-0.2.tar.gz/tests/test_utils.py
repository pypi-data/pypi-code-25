import pytest

from termstree import utils


def test_parse_kv_pairs():
    s = 'key1=value1 "key 2"="value 2"'
    assert {'key1': 'value1', 'key 2': 'value 2'} == utils.parse_kv_pairs(s)
    assert {} == utils.parse_kv_pairs('')

def test_parse_kv_pairs_error():
    s = 'key1=value 1 "key 2"="value 2"'
    with pytest.raises(ValueError) as ex:
        print(utils.parse_kv_pairs(s))


def test_parse_kv_pairs_error_space_after_equal_sign():
    s = 'key1=value1 "key 2"= "value 2"'
    with pytest.raises(ValueError) as ex:
        print(utils.parse_kv_pairs(s))
