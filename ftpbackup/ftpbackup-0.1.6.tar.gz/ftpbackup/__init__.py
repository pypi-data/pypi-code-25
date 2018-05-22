# -*- coding: utf-8 -*-

import os
import pathspec
import argparse
import json
from ftplib import FTP
import ftplib

from . import json_cleaner

__VERSION__ = "0.1.6"

__DEFAULT_CONF__ = """{
    "protocol": "ftp", // string - Only 'ftp' now.
    "host": "localhost", // string - The hostname or IP address of the FTP server. Default: 'localhost'
    "encoding": "utf-8", // string - The encoding of the FTP server. Default: utf-8
    "port": 21, // integer - The port of the FTP server. Default: 21
    "user": "anonymous", // string - Username for authentication. Default: 'anonymous'
    "pass": "anonymous@", // string - Password for authentication. Default: 'anonymous@'
    "remote": "/", // string - The path on FTP to upload files.
    // NOTE : Use absolute path of remote or get a error.
    "local": ".", // string - The folder on local to be uploaded.
    "useGitIgnore": true, // bool - Use .gitignore in ignored file list.
    "gitIgnoreEncoding": "utf-8", // string - The encoding of .gitignore
    "useFtpIgnore": true, // bool - Use .ftpignore in ignored file list.
    "ftpIgnoreEncoding": "utf-8" // string - The encoding of .ftpignore
}
"""

class Config():
    def __init__(self, file = None):
        if file is None:
            pass
        elif not os.path.exists(file):
            raise FileNotFoundError('Can\'t find config file "' + file + '"')
        else:
            with open(file, 'r', encoding='UTF-8') as fh:
                self.loadText(fh.read())

    def loadText(self, text):
        confText = json_cleaner.remove_comments(text)
        confDist = json.loads(confText)
        self.checkAndLoadDist(confDist)

    def checkAndLoadDist(self, confDist):
        # protocol
        if type(confDist['protocol']) is not str:
            raise Exception("config parameter \"protocol\" is error, plz check config file")
        elif confDist['protocol'] == '':
            self.protocol = 'ftp'
        elif confDist['protocol'] != 'ftp':
            raise Exception("unsupport portocol :" + confDist['protocol'])
        else:
            self.protocol = confDist['protocol']
        # host
        if type(confDist['host']) is not str:
            raise Exception("config parameter \"host\" is error, plz check config file")
        elif confDist['host'] == '':
            self.host = 'localhost'
        else:
            self.host = confDist['host']
        # port
        if type(confDist['port']) is not int:
            raise Exception("config parameter \"port\" is error, plz check config file")
        else:
            self.port = confDist['port']
        # user
        if type(confDist['user']) is not str:
            raise Exception("config parameter \"user\" is error, plz check config file")
        elif confDist['user'] == '':
            self.user = 'anonymous'
        else:
            self.user = confDist['user']
        # pass
        if type(confDist['pass']) is not str:
            raise Exception("config parameter \"pass\" is error, plz check config file")
        elif confDist['pass'] == '':
            self.passwd = 'anonymous@'
        else:
            self.passwd = confDist['pass']
        # encoding
        if type(confDist['encoding']) is not str:
            raise Exception("config parameter \"encoding\" is error, plz check config file")
        elif confDist['encoding'] == '':
            self.encoding = 'utf8'
        else:
            self.encoding = confDist['encoding']
        # remote
        if type(confDist['remote']) is not str:
            raise Exception("config parameter \"remote\" is error, plz check config file")
        elif confDist['remote'] == '':
            self.remote = '.'
        else:
            self.remote = confDist['remote']
        # local
        if type(confDist['local']) is not str:
            raise Exception("config parameter \"local\" is error, plz check config file")
        elif confDist['local'] == '':
            self.local = '.'
        else:
            self.local = confDist['local']
        # useGitIgnore
        if type(confDist['useGitIgnore']) is not bool:
            raise Exception("config parameter \"useGitIgnore\" is error, plz check config file")
        else:
            self.useGitIgnore = confDist['useGitIgnore']
        # gitIgnoreEncoding
        if type(confDist['gitIgnoreEncoding']) is not str:
            raise Exception("config parameter \"gitIgnoreEncoding\" is error, plz check config file")
        elif confDist['gitIgnoreEncoding'] == '':
            self.gitIgnoreEncoding = 'utf-8'
        else:
            self.gitIgnoreEncoding = confDist['gitIgnoreEncoding']
        # useFtpIgnore
        if type(confDist['useFtpIgnore']) is not bool:
            raise Exception("config parameter \"useFtpIgnore\" is error, plz check config file")
        else:
            self.useFtpIgnore = confDist['useFtpIgnore']
        # ftpIgnoreEncoding
        if type(confDist['ftpIgnoreEncoding']) is not str:
            raise Exception("config parameter \"ftpIgnoreEncoding\" is error, plz check config file")
        elif confDist['ftpIgnoreEncoding'] == '':
            self.ftpIgnoreEncoding = 'utf-8'
        else:
            self.ftpIgnoreEncoding = confDist['ftpIgnoreEncoding']

class FtpBackup():
    def __init__(self, conf):
        self._conf = conf
        self._connectFtp()
        self._loadIgnoreFiles()

    def _connectFtp(self):
        self._ftp = ftplib.FTP()
        self._ftp.encoding = self._conf.encoding
        self._ftp.connect(self._conf.host, self._conf.port)
        self._ftp.login(self._conf.user, self._conf.passwd)

    def _loadIgnoreFiles(self):
        text = str()
        if self._conf.useGitIgnore:
            file = '.gitignore'
            encode = self._conf.gitIgnoreEncoding
            if not os.path.exists(file):
                print('Can\'t find ignore file "'+file+'".')
            else:
                with open(file, encoding=encode) as fh:
                    text = text + '\n' + fh.read()
        if self._conf.useFtpIgnore:
            file = '.ftpignore'
            encode = self._conf.ftpIgnoreEncoding
            if not os.path.exists(file):
                print('Can\'t find ignore file "'+file+'".')
            else:
                with open(file, encoding=encode) as fh:
                    text = text + '\n' + fh.read()
        self._spec = pathspec.PathSpec.from_lines(pathspec.GitIgnorePattern, text.splitlines())

    def startBackup(self):
        rootdir = self._conf.local
        remote = self._conf.remote
        list_dirs = os.walk(rootdir)
        print('try to make dir "' + remote + '"... ', end='')
        try:
            self._ftp.mkd(remote)
        except UnicodeDecodeError as e:
            pass
        except ftplib.error_perm :
            pass
        print('Complete!')
        for root, dirs, files in list_dirs:
            if not isMatchSpec(root+'\\', self._spec):
                # print('root = ' + root)
                # print('remote = ' + (remote + root[1:len(root)].replace('\\', '/')))
                remotedir = remote + root[1:len(root)].replace('\\', '/')
                self._ftp.cwd(remotedir)
                print('enter dir: "' + remotedir + '"')
                for dir in dirs:
                    if not isMatchSpec(dir+'\\', self._spec):
                        # print('  - dir = ' + dir)
                        print('try to make dir "' + dir + '"... ', end='')
                        try:
                            self._ftp.mkd(dir)
                        except UnicodeDecodeError as e:
                            pass
                        except ftplib.error_perm :
                            pass
                        print('Complete!')
                for file in files:
                    # print('  - file = ' + file)
                    print('upload file "' + os.path.join(root, file) + '"... ', end='')
                    with open(os.path.join(root, file), 'rb') as fp:
                        self._ftp.storbinary('STOR '+file, fp, blocksize=8192, callback=None, rest=None)
                    print('Complete!')

def isMatchSpec(s ,spec):
    if len(set(spec.match_files([s]))) is 0:
        return False
    else:
        return True
