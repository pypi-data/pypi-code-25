# -*- coding=utf-8 -*-

import requests
import re
import time
import logging


class YZM360:
    token = None

    def __init__(self, username, password, uid, pid):
        self.username = username
        self.password = password
        self.uid = uid
        self.pid = pid
        self.logger = logging.getLogger()
        self.login()

    def login(self):
        params = {
            "uname": self.username,
            "pwd": self.password,
            "author_uid": self.uid
        }
        res = requests.get("http://api.360yzm.com/user.do!loginIn", params=params)
        self.token = res.content.split("|")[1]
        return self.token

    def get_phone(self):
        """
        正确返回：1|手机号码
        返回多个手机号的时候，用分号分隔，如：15999514842;13210729083
        token过期返回：0|token过期
        余额不足返回：0|余额不足
        :param token: 
        :return: 
        """
        params = {
            "pid": self.pid,
            "token": self.token
        }
        res = requests.get("http://api.360yzm.com/user.do!getPhone", params=params)
        content = res.content
        if re.search("^1\|", content):
            # ok
            return content.split("|")[1]
        else:
            return ""

    def get_sms_content(self, _phone):
        t = 0
        while t < 10:
            sms_content = self.get_sms(_phone)
            if sms_content:
                return sms_content
            else:
                t += 1
                time.sleep(3)

    def get_sms(self, _phone):
        params = {
            "pid": self.pid,
            "token": self.token,
            "phone": _phone
        }
        res = requests.get("http://api.360yzm.com/user.do!getMessage?", params=params)
        content = res.content
        if re.search("^1\|", content):
            # ok
            return content.split("|")[1]
        else:
            return 0


if __name__ == "__main__":
    pass
