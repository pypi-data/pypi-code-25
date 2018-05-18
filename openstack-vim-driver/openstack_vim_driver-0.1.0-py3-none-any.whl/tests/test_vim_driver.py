import pytest
from unittest.mock import patch, MagicMock, Mock, mock_open
from openstack_vim_driver.openstack_vim_driver import OpenstackVimDriver

import builtins
import os.path
import io
from itertools import cycle

vim_driver = OpenstackVimDriver(True, 10, 15, '/net/u/tbr/Desktop/asdfasdfasdfsadf')

# def mock_exists(file_path):
#     return True
#
#
# mock_open = Mock(return_value=MagicMock(spec=io.IOBase))
#
# file = Mock(spec=io.TextIOWrapper())
# file.__iter__ = ['line1', 'line2', 'line3']
#
# @mock.patch('os.path.exists', side_effect=mock_exists)
# @mock.patch('builtins.open', side_effect=mock_open)
# def test_translate_to_nat(mock_exists, mock_open):
#     fip = vim_driver.translate_to_nat('192.168.2.120')
#     print(fip)
#     assert fip == '192.168.2.120'







@pytest.mark.parametrize('floating_ip,expected', [('172.20.17.4', '172.20.17.4')])
@patch('builtins.open')
@patch('os.path.exists', return_value=True)
def test_some(mock_exists, mock_open_file, floating_ip, expected):
    mock_open(mock_open_file, ("""172.20.16.0/24 = 10.5.20.0/24
                              172.20.17.0/24 = 10.5.21.0/24"""))
    assert vim_driver.translate_to_nat(floating_ip) == expected





    # mock_open.side_effect = [
    #     mock_open(read_data="Data1").return_value,
    #     mock_open(read_data="Data2").return_value
    # ]
    #
    # self.assertEqual("Data1", some("fileA"))
    # mock_open.assert_called_once_with("fileA")
    # mock_open.reset_mock()
    #
    # self.assertEqual("Data2", some("fileB"))
    # mock_open.assert_called_once_with("fileB")