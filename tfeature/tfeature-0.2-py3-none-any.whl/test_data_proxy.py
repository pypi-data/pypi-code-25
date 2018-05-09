from .context import zen
import zen.data_proxy as data
from zen.const import DAY, DAY_IX, MINUTE, MINUTE_IX


def test_choose_file():
    assert data.choose_file(freq='D', asset='E') == DAY
    assert data.choose_file(freq='D', asset='INDEX') == DAY_IX
    assert data.choose_file(freq='1min', asset='E') == MINUTE
    assert data.choose_file(freq='1min', asset='INDEX') == MINUTE_IX


def test_get_local_data():
    assert len(
        data.get_local_data(
            '000001', asset='INDEX', start='20171120', end='20171201')) == 10
    assert len(
        data.get_local_data(
            '000002', asset='INDEX', start='20171120', end='20171201')) == 10
    assert len(
        data.get_local_data('000002', asset='E', start='20171120',
                       end='20171201')) == 10
    assert len(
        data.get_local_data('600604', asset='E', start='20171120',
                       end='20171201')) == 10


def test_get_index_stocks():
    assert '300127.SZ' in data.get_index_stocks(c_name='新材料')
    assert '002340.SZ' in data.get_index_stocks(c_name='新材料')
    assert '002340.SZ' in data.get_index_stocks(c_code='881114.TI')
    assert '000001.SZ' not in data.get_index_stocks(c_name='新材料')
    assert len(data.get_index_stocks('881114.TI')) == 34

def test_ccode_to_cname():
    assert data.ccode_to_cname('885311.TI') == '智能电网'
    assert data.ccode_to_cname('885461.TI') == '充电桩'

def test_cname_to_ccode():
    assert data.cname_to_ccode('光伏概念') == '885531.TI'
    assert data.cname_to_ccode('电气设备') == '881120.TI'

def test_all_boards():
    assert len(data.all_boards()) == 255

def test_all_stocks():
    assert len(data.all_stocks()) == 3470
