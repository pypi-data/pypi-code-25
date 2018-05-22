# -*- coding: utf-8 -*-

import os
import pathspec
import argparse
import json
from ftplib import FTP
import ftplib

from . import json_cleaner

__VERSION__ = "0.1.0"

__DEFAULT_CONF__ = """{
    "protocol": "ftp",
    "host": "localhost", // string - The hostname or IP address of the FTP server. Default: 'localhost'
    "port": 21, // integer - The port of the FTP server. Default: 21
    "user": "anonymous", // string - Username for authentication. Default: 'anonymous'
    "pass": "anonymous@", // string - Password for authentication. Default: 'anonymous@'
    "encoding": "big5",
    "remote": ".",
    "local": ".",
    "useGitIgnore": true,
    "gitIgnoreEncoding": "utf-8",
    "useFtpIgnore": true,
    "ftpIgnoreEncoding": "utf-8"
}
"""

class Config():
    def __init__(self, file):
        if not os.path.exists(file):
            raise FileNotFoundError('Can\'t find config file "' + file + '"')
        else:
            with open(file, 'r', encoding='UTF-8') as fh:
                confText = json_cleaner.remove_comments(fh.read())
            confDist = json.loads(confText)

    def checkAndLoadDist(self, confDist):
        pass


class FtpBackup():
    def __init__(self, config):
        pass
