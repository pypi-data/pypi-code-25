# my_scp.py
# Copyright (C) 2018 Zhao XueQing <729125866@qq.com>

"""
Utilities for sending files over ssh using the scp1 protocol.
"""

__version__ = '2018.5.17'

import paramiko
from scp import SCPClient

def get_connection(hostname, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)
    return ssh

class My_Scp(object):
    def __init__(self):
        pass
    def my_put(self,username,password,local_path,remote_path,hostname,port=22):
        ssh = get_connection(hostname, port, username, password)
        scp = SCPClient(ssh.get_transport())
        scp.put(local_path, remote_path)
        ssh.close()
        scp.close()
    def my_get(self,username,password,local_path,remote_path,hostname,port=22):
        ssh = get_connection(hostname, port, username, password)
        scp = SCPClient(ssh.get_transport())
        scp.get(local_path, remote_path)
        ssh.close()
        scp.close()