# -*- coding: utf-8 -*-
import requests
import os
import time
import base64
from mtianyan.path_helper import path_file_existed_or_create

class Aria2JsonRpc(object):
    def __init__(self, rpc_url, arai2_path):
        # assert_path = ['./dir/',
        #                 './out/']
        # path_file_existed_or_create(assert_path)
        # RPC采用客户机/服务器模式。 请求程序就是一个客户机，而服务提供程序就是一个服务器。 首先，调用进程发送一个有进程参数的调用信息到服务进程，然后等待应答信息。
        # 初始化时指定rpc地址: http://localhost:6800/jsonrpc?tm=%s
        self.rpc_url = rpc_url
        # 指定可执行文件地址: ./
        self.arai2_path = arai2_path
        # 如果rpc服务未开启, 那么启动。
        if not self.isAlive():
            self.startAria2Rpc()


    def isAlive(self):
        """
        判断rpc服务是否激活
        """
        # 生成一个payload: payload 可以理解为一系列信息中最为关键的信息。
        payload = {"jsonrpc": "2.0", "method": "aria2.tellActive", "id": 1}
        # 时间戳签名
        tm = int(time.time() * 1000)
        url = self.rpc_url % str(tm)
        try:
            r = requests.get(url, payload)
            return r.status_code == 200
        except Exception:
            return False


    def startAria2Rpc(self):
        """
        开启rpc服务
        """
        # 启动命令写入文件
        download_helper_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'download_helper')
        bat_path = download_helper_path + '\startAria2Rpc.bat'
        launch_file = open(bat_path, "w")
        print(bat_path)
        new_cmd = "aria2c.exe --conf-path=aria2.conf -D"
        launch_file.write(new_cmd)
        launch_file.close()
        # aria2 使用cmd打开
        os.chdir(download_helper_path)
        os.startfile(bat_path)
        print('****')
        # 进程挂起3秒保证aria2打开完毕
        time.sleep(3)

    def execuetJsonRpcCmd(self, method, param=None):
        """
        执行命令函数
        """
        payload = {"jsonrpc": "2.0", "method": method, "id": 1, "params": param}
        payloads = [payload]
        tm = int(time.time() * 1000)
        url = self.rpc_url % str(tm)
        print(payloads)
        r = requests.post(url, None, payloads)
        print(r.text)
        return r.status_code

    

    def addUris(self, urls, dir=None, out=None):
        params = []
        download_config = {}
        if dir:
            download_config["dir"] = dir
        if out:
            download_config["out"] = out
        params.append(urls)
        params.append(download_config)
        print(self.execuetJsonRpcCmd("aria2.addUri", params))

    def addTorrent(self, path, dir=None, out=None):
        bits = open(path, "rb").read()
        torrent = base64.b64encode(bits)
        params = []
        download_config = {"dir": dir, "out": out}
        params.append(torrent)
        params.append([])
        params.append(download_config)
        print(self.execuetJsonRpcCmd("aria2.addTorrent", params))

def via_urls(download_list,dir,filename=None):
    aria2_path = "./"
    rpc_url = "http://localhost:6800/jsonrpc?tm=%s"
    # 启动服务
    rpcClient = Aria2JsonRpc(rpc_url, aria2_path)
    os_path = os.getcwd()
    download_path = os.path.join(os_path,dir[2:])
    for url in download_list:
        # 添加下载任务
        rpcClient.addUris([url],download_path,filename)

if __name__ == '__main__':
    magnet = ['http://groups.inf.ed.ac.uk/vision/CAVIAR/CAVIARDATA1/Browse3/Browse3_jpg.tar.gz',
                'http://groups.inf.ed.ac.uk/vision/CAVIAR/CAVIARDATA1/Browse4/Browse4_jpg.tar.gz']
    rpc_url = "http://localhost:6800/jsonrpc?tm=%s"
    aria2_path = "./"
    # 启动服务
    rpcClient = Aria2JsonRpc(rpc_url, aria2_path)
    # 添加下载任务
    # rpcClient.addUris(magnet,'./dir/')
    via_urls(magnet,'./dir')
