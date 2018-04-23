# -*- coding: utf-8 -*-
"""bug问题相关处理和收集"""

import os
import traceback
import faulthandler
import sys
import uuid
import json
import time
from threading import Thread

self_path = os.path.dirname(sys.argv[0])

log_file = os.path.join(self_path, 'logs/error.log')
bug_file = os.path.join(self_path, 'logs/bug.log')


def enable_bug_collect():
    if not os.path.exists(os.path.dirname(log_file)):
        os.mkdir(os.path.dirname(log_file))

    faulthandler.enable(file=open((log_file), "wb"), all_threads=True)


class BugStruct(object):

    def __init__(self):
        super(BugStruct, self).__init__()
        self.data = ''
        self.md5_value = None

    def md5(self):
        if self.md5_value:
            return self.md5_value

        import hashlib
        m2 = hashlib.md5()
        m2.update(self.data.encode())
        self.md5_value = m2.hexdigest()
        return self.md5_value

    def clear(self):
        """
        清理MD5日志
        """
        filename = 'logs/.{}'.format(self.md5())
        os.remove(filename)

    def append_dump(self):
        """
        追加写入到日志文件
        """
        with open(bug_file, 'ab') as f:
            f.write(b'\n\n\n')
            f.write(self.data.encode())

    def dump(self):
        """
        保存MD5文件 为了去重和二次post
        :return:
        """
        filename = 'logs/.{}'.format(self.md5())
        if os.path.exists(filename):
            return

        with open(filename, 'wb') as f:
            print('dump..')
            f.write(self.data.encode())

        self.append_dump()

    def set_data(self, data):
        self.data = data

    @classmethod
    def version(cls):
        """
        读取主程序版本信息
        :return:
        """
        root_dir = ''
        version_dat = os.path.join(root_dir, 'version.dat')
        if os.path.exists(version_dat):
            with open(version_dat, 'r') as f:
                value = json.load(f)
                return value.get('version', '?'), value.get('mode', '?')

        else:
            return '?', '?'

    def machine_info(self):
        """
        获取机器信息
        :rtype: object
        """
        return {}

    def mac_addres(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    def post(self, url):
        version_str, version_mode = self.version()

        post_data = {'version_str': version_str,
                     'version_mode': version_mode,
                     'machine_info': self.machine_info(),
                     'mac_addres': self.mac_addres(),
                     'data': self.data,
                     }

        import requests
        req = requests.post(url, data=post_data)

        if req.status_code == 200:
            self.clear()


class BugSubmit(Thread):

    def __init__(self, api_url):
        super(BugSubmit, self).__init__()
        import queue
        self.queue = queue.Queue()

        self.api_url = api_url

        self.bug_md5_lst = []
        self.current_post_bug = None
        self.post = True

    def is_null(self):
        if self.queue.empty() and not self.current_post_bug:
            return True

    def set_post(self, status):
        self.post = status

    def put(self, bug_obj):
        self.queue.put(bug_obj)

    def run(self):
        enable_bug_collect()

        while 1:
            bug = self.queue.get()

            if self.post:

                self.current_post_bug = bug

                try:
                    if bug.md5() not in self.bug_md5_lst:
                        bug.post(self.api_url)
                        self.bug_md5_lst.append(bug.md5())

                except BaseException as e:
                    print(e)

                self.current_post_bug = None

                with open(log_file, 'rb') as f:
                    data = f.read()
                    bug_obj = BugStruct()
                    bug_obj.set_data(data)
                    bug_obj.dump()

                    self.put(bug_obj)

                time.sleep(2)


class BugHook(object):

    def __init__(self, dump_file=True, post_url=True, pprint=True):
        super(BugHook, self).__init__()

        self.dump_file = dump_file
        self.pprint = pprint

        self.post_thread = BugSubmit(post_url)
        self.post_thread.setDaemon(True)
        self.post_thread.set_post(post_url)

        sys.excepthook = self.handle_exception

    def start(self):
        self.post_thread.start()

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        data = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        if self.pprint:
            print(data)

        bug_obj = BugStruct()
        bug_obj.set_data(data)
        if self.dump_file:
            bug_obj.dump()

        self.post_thread.put(bug_obj)


if __name__ == '__main__':
    a = BugHook(
        dump_file=True,
        post_url='',
        # post_url='http://version.api.xiadele.com/api/bug',
        pprint=True)
    a.start()

    a.post_thread.join()
