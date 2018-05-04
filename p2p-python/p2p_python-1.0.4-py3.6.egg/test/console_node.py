#!/user/env python3
# -*- coding: utf-8 -*-

from p2p_python.config import C, V, Debug
from p2p_python.utils import setup_p2p_params
from p2p_python.client import PeerClient, ClientCmd
from test.tool import f_already_bind, get_logger
import random
import logging
import time
import pdb


def broadcast_check(data):
    print(data)
    return True


def work():
    if f_already_bind(2000):
        port = random.randint(2001, 3000)
        sub_dir = 'test{}'.format(port)
        setup_p2p_params(network_ver=12345, p2p_port=port, p2p_accept=True, sub_dir=sub_dir)
    else:
        port = 2000
        setup_p2p_params(network_ver=12345, p2p_port=port, p2p_accept=True)
    Debug.P_EXCEPTION = True
    get_logger(level=logging.DEBUG)
    pc = PeerClient()
    pc.start()
    pc.broadcast_check = broadcast_check
    if port != 2000:
        pc.p2p.create_connection(host='127.0.0.1', port=2000)
    else:
        time.sleep(5)
        while True:
            input('>>')
            print(pc.send_command(ClientCmd.BROADCAST, data='hello world'))
        pass
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
[user.name for user in pc.p2p.user]
pc.send_command(ClientCmd.PING_PONG, data=time.time())
pc.send_command(ClientCmd.BROADCAST, data='hello world')
pc.send_command(ClientCmd.CHECK_REACHABLE, data={'port':1234})
"""