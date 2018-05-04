#!/user/env python3
# -*- coding: utf-8 -*-

from p2p_python.config import C, V, Debug
from p2p_python.utils import setup_p2p_params
from p2p_python.client import PeerClient, ClientCmd
from p2p_python.tool.share import FileShare
from test.tool import f_already_bind, get_logger
import random
import logging
import os


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
    if port != 2000:
        pc.p2p.create_connection(host='127.0.0.1', port=2000)
        fs = FileShare(pc, path=os.path.join(V.DATA_PATH, 'movie.mp4.share'))

    else:
        pass
        fs = FileShare(pc, path=os.path.join(V.DATA_PATH, 'movie.mp4'))
        fs.share_raw_file()
        fs.recode_share_file()
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
fs.load_share_file()
fs.download()
fs.recode_raw_file(V.DATA_PATH)
pc.send_command(ClientCmd.FILE_CHECK, {'hash': '94bb377f1c505784c47b899d8a2e492fd111d49231b631f7ee5b7c0284c41be1', 'uuid': 0})
pc.get_file('94bb377f1c505784c47b899d8a2e492fd111d49231b631f7ee5b7c0284c41be1')
"""