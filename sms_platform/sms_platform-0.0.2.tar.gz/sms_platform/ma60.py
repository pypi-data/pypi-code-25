# -*- coding=utf-8 -*-
import hashlib
import requests
import time
import logging


def md5(_str):
    hash_md5 = hashlib.md5(_str)
    return hash_md5.hexdigest()


class MA60:
    token = None

    def __init__(self, username, password, uid, pid):
        self.username = username
        self.password = password
        self.uid = uid
        self.pid = pid
        self.logger = logging.getLogger()
        self.login()

    def __get_param(self):
        return {
            "userid": self.uid,
            "userkey": self.token,
            "docks": self.pid,
            "dockcode": self.pid,
            "dtype": "json",
            "encode": "utf-8"
        }

    def login(self):
        params = {
            "username": self.username,
            "password": md5(self.password),
            "dtype": "json",
            "cmd": "login",
            "encode": "utf-8"
        }
        res = requests.get("http://sms.60ma.net/loginuser", params=params).json()
        self.token = res["Return"]["UserKey"]
        return self.token

    def get_phone(self):
        params = self.__get_param()
        params["cmd"] = "gettelnum"
        res = requests.get("http://sms.60ma.net/newsmssrv", params=params).json()
        if res["Return"]["Staus"] == '0':
            return res["Return"]["Telnum"]
        else:
            self.logger.error("get phone fail " + res["Return"]["ErrorInfo"])
            return False

    def get_sms_content(self, _phone):
        t = 0
        while t < 10:
            sms_content = self.get_sms(_phone)
            if sms_content:
                return sms_content
            else:
                t += 1
                time.sleep(3)
        # 释放号码
        self.release(_phone)
        return ""

    def release(self, _phone):
        params = self.__get_param()
        params["telnum"] = _phone
        params["cmd"] = "freetelnum"
        requests.get("http://sms.60ma.net/newsmssrv", params=params)

    def get_sms(self, _phone):
        params = self.__get_param()
        params["telnum"] = _phone
        params["cmd"] = "getsms"
        res = requests.get("http://sms.60ma.net/newsmssrv", params=params)
        try:
            res = res.json()
        except Exception as e:
            self.logger.error(e)
            return False
        if res["Return"]["Staus"] == '0':
            return res["Return"]["SmsContent"]
        else:
            self.logger.error("get sms fail " + res["Return"]["ErrorInfo"])
            return False
