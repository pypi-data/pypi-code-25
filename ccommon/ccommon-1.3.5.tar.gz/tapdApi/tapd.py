#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/10 9:35
# @Author  : chenjw
# @Site    : 
# @File    : tapd.py
# @Software: PyCharm Community Edition
# @Desc    :  do what

from requests import auth
import time
import threading


class Tapd:
    def __init__(self, usr, pwd,delay=1000):
        self.usr = usr
        self.pwd = pwd
        self.delay = delay
        self.lastRequestTime = 0
        self.lock = threading.Lock()

    def retAuth(self):
        return auth.HTTPBasicAuth(self.usr, self.pwd)

    def checkApiStatus(self,_json):
        if _json.Int('status') != 1:
            raise Exception('[Tapd] checkApiStatus eager %s but indeed %s' % (1,_json.Int('status')))

    # 时间戳 毫秒
    def now(self):
        return int(round(time.time()*1000))


    def wait(self):
        self.lock.acquire(1)
        try:
            if self.lastRequestTime == 0:
                self.lastRequestTime = self.now()
            else:
                sub_time = self.now() - self.lastRequestTime
                if sub_time < self.delay:
                    time.sleep(float(sub_time) / float(1000))
                self.lastRequestTime = self.now()
        except:
            pass
        finally:
            self.lock.release()





if __name__ == '__main__':

    pass