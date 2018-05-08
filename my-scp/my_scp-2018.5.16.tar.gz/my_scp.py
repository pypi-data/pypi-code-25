# my_scp.py
# Copyright (C) 2018 Zhao XueQing <729125866@qq.com>

"""
Utilities for sending files over ssh using the scp1 protocol.
"""

__version__ = '2018.5.16'

import threading
import paramiko
from scp import SCPClient

def get_ssh_connect(ip, username, password, port='22'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port,username,password)
    return ssh
def scp_send(ssh,frompath,topath):
    scp = SCPClient(ssh.get_transport())
    scp.put(frompath,topath)
    scp.close()
def deploy(ip,port,username,password,frompath,topath):
    ssh = get_ssh_connect(ip, port, username, password)
    scp_send(ssh, frompath, topath)
def scp_put(username,password,frompath,topath,port=22,*hostname):
    threads = []  # 运行的线程列表
    for ip in hostname:
        t = threading.Thread(target=deploy,args=(ip,port,username,password,frompath,topath))
        threads.append(t)  # 将子线程追加到线程列表
    for t in threads:
        t.start()
        t.join()

if __name__ == "__main__":
    pass
    #main()