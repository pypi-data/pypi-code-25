from pytrello.api import util
from pytrello.api import board as board_api
from nose.tools import raises


@raises(SystemExit)
def test_get_board_id_fail():
    util.get_board_id('pytrell')


def test_get_board_id_success():
    util.get_board_id('pytrello')


def test_get_board_labels():
    board_id = util.get_board_id('pytrello')
    labels = board_api.get_board_labels(board_id=board_id)
    names = [label['name'] for label in labels]

    assert 'urgent' in names


@raises(SystemExit)
def test_get_label_id_fail():
    util.get_label_id(board_name='pytrello', label_name='urgen')


def test_get_label_id_success():
    util.get_label_id(board_name='pytrello', label_name='urgent')
