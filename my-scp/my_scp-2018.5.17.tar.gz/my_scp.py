# my_scp.py
# Copyright (C) 2018 Zhao XueQing <729125866@qq.com>

"""
Utilities for sending files over ssh using the scp1 protocol.
"""

__version__ = '2018.5.17'

import paramiko
from scp import SCPClient

class My_Scp(object):
    def __init__(self,username,password,local_path,remote_path,hostname,port=22):
        self.username = username
        self.password = password
        self.local_path = local_path
        self.remote_path   = remote_path
        self.hostname = hostname
        self.port = port

    def my_put(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, self.port, self.username, self.password)
        scp = SCPClient(ssh.get_transport())
        scp.put(self.local_path, self.remote_path)
        scp.close()
    def my_get(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, self.port, self.username, self.password)
        scp = SCPClient(ssh.get_transport())
        scp.get(self.local_path, self.remote_path)
        scp.close()