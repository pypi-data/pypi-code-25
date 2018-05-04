#!/user/env python3
# -*- coding: utf-8 -*-

from p2p_python.config import C, V, Debug
from p2p_python.utils import setup_p2p_params
from p2p_python.client import PeerClient, ClientCmd
from test.tool import f_already_bind, get_logger
import random
import logging


def broadcast_check(data):
    print("broadcast_check", data)
    if len(data) % 2 == 0:
        return True
    else:
        print("stop!")
        return False


def work():
    Debug.P_EXCEPTION = True
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
    pc.broadcast_check = broadcast_check
    if port != 2000:
        pc.p2p.create_connection(host='127.0.0.1', port=2000)
    else:
        pass
    logging.info("Connect as {}".format(port))
    # 接続済み

    while True:
        try:
            cmd = input('>> ')
            exec("print("+cmd+")")
        except EOFError:
            break
        except TimeoutError as e:
            print("timeout", e)
        except Exception:
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    work()

"""
[user.name for user in pc.p2p.user]
pc.send_command(ClientCmd.BROADCAST, data='hello world')
"""