import sys
from mock import patch, mock_open
import pytest
from ardexa_check_active import fix_dns

python3_only = pytest.mark.skipif(sys.version_info < (3, 0),
                                  reason="requires Python3")
python2_only = pytest.mark.skipif(sys.version_info >= (3, 0),
                                  reason="requires Python2")

def test_fix_dns_all_good():
    arr = [None] * 9
    arr[5] = 'good'
    arr[8] = 'good'
    assert fix_dns(arr) is False

def test_fix_dns_all_bad():
    arr = [None] * 9
    arr[5] = 'bad'
    arr[8] = 'bad'
    assert fix_dns(arr) is False

@python2_only
def test_fix_dns_bad_local2():
    arr = [None] * 9
    arr[5] = 'bad'
    arr[8] = 'good'
    result = False
    with patch("__builtin__.open", mock_open()) as mock_file:
        result = fix_dns(arr)
        mock_file.assert_called_with("/etc/resolv.conf", "w")
    assert result

@python3_only
def test_fix_dns_bad_local3():
    arr = [None] * 9
    arr[5] = 'bad'
    arr[8] = 'good'
    result = False
    with patch("builtins.open", mock_open()) as mock_file:
        result = fix_dns(arr)
        mock_file.assert_called_with("/etc/resolv.conf", "w")
    assert result

def test_fix_dns_bad_local():
    arr = [None] * 9
    arr[5] = 'bad'
    arr[8] = 'good'
    result = False
    builtin_open = "builtins.open"
    if sys.version_info < (3, 0):
        builtin_open = "__builtin__.open"
    with patch(builtin_open, mock_open()) as mock_file:
        result = fix_dns(arr)
        mock_file.assert_called_with("/etc/resolv.conf", "w")
        mock_file().write.assert_called_with("nameserver 8.8.8.8\n")
    assert result
