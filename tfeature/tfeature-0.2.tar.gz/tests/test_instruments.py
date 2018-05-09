from .context import zen
import zen.instruments as its
import pytest


@pytest.fixture(scope='function')
def index():
    return its.Index


@pytest.fixture(scope='function')
def stock():
    return its.Stock

@pytest.fixture(scope='function')
def board():
    return its.Board

@pytest.fixture(scope='function')
def all_instruments():
    return its.AllInstruments


def test_index(index):
    sh = index('000001')
    sz = index('399001')
    cyb = index('399006')

    assert sh.secid == '000001'
    assert sh.ma_rating(date='20171208') == (8, 2)

    assert sz.secid == '399001'
    assert sz.ma_rating(date='20171208') == (8, 3)

    assert cyb.secid == '399006'
    assert cyb.asset == 'INDEX'
    assert cyb.ma_rating(date='20171208') == (2, 2)


def test_stock(stock):
    swtx = stock('002405')
    hsdq = stock('300141')

    assert swtx.ma_rating(date='20171208') == (8, 4)
    assert hsdq.ma_rating(date='20171208') == (1, 1)
    assert sorted(hsdq.boards().c_name.values) == sorted(['充电桩', '电气设备', '光伏概念', '智能电网'])

def test_board(board):
    zndw = board(c_name='智能电网')
    cdz = board('885461.TI')
    ai = board('885728.TI')

    assert zndw.c_code == '885311.TI'
    assert cdz.c_name == '充电桩'
    assert ai.c_name == '人工智能'

    assert '300141.SZ' in cdz.stocks()
    assert '002405.SZ' in ai.stocks()

    # assert ai.ma_rating(date='20171208') == (3, 2)
    # assert cdz.ma_rating(date='20171208') == (2, 1)
    # assert zndw.ma_rating(date='20171208') == (2, 2)

def test_all_instruments(all_instruments):
    assert len(all_instruments().boards()) == 255
    assert len(all_instruments().stocks()) >= 3470
