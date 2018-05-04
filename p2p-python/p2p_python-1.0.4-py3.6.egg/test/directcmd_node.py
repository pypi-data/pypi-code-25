#!/user/env python3
# -*- coding: utf-8 -*-

from p2p_python.config import C, V, Debug
from p2p_python.utils import setup_p2p_params
from p2p_python.client import PeerClient, ClientCmd
from test.tool import f_already_bind, get_logger
import random
import logging
import time


class DirectCmd:
    WHAT_IS_YOUR_NAME = 'cmd/ac/what-your-name'
    GET_TIME_NOW = 'cmd/ac/get-time-now'


def what_is_your_name(data):
    print("what_is_your_name", data)
    return time.time() // 1000


def get_time_now(data):
    print("get_time_now", data)
    return time.time()


def work():
    if f_already_bind(2000):
        port = random.randint(2001, 3000)
        sub_dir = 'test{}'.format(port)
        setup_p2p_params(network_ver=12345, p2p_port=port, p2p_accept=True, sub_dir=sub_dir)
    else:
        port = 2000
        setup_p2p_params(network_ver=12345, p2p_port=port, p2p_accept=True)
    get_logger(level=logging.DEBUG)
    pc = PeerClient()
    pc.start()
    if port != 2000:
        pc.p2p.create_connection(host='127.0.0.1', port=2000)
    else:
        pass
    pc.event.addevent(DirectCmd.WHAT_IS_YOUR_NAME, what_is_your_name)
    pc.event.addevent(DirectCmd.GET_TIME_NOW, get_time_now)
    Debug.P_EXCEPTION = True
    logging.info("Connect as {}".format(port))
    # 接続済み

    while True:
        try:
            cmd = input('>> ')
            exec("print("+cmd+")")
        except EOFError:
            break
        except Exception as e:
            print(e)


if __name__ == '__main__':
    work()

"""
pc.send_direct_cmd(DirectCmd.WHAT_IS_YOUR_NAME, 'hello?')
pc.send_direct_cmd(DirectCmd.GET_TIME_NOW, 'hello!')
pc.send_direct_cmd(DirectCmd.WHAT_IS_YOUR_NAME, 'hello?', 'user/direct')
"""