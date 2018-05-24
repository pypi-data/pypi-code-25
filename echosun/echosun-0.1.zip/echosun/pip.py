#!/usr/bin/env python
# coding=utf-8
import platform
import os


def make_dir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print(path + ' Create finish.')
        return True
    else:
        print(path + ' Directory already exists.')
        return False


def make_file(filePath):
    pipfile = "[global]\ntrusted-host=mirrors.aliyun.com\nindex-url=http://mirrors.aliyun.com/pypi/simple/"
    if os.path.exists(filePath):
        if str(input("File exist!Cover?(Y/N))")).upper() == 'N':
            print("Not Cover.")
            return
    with open(filePath, 'w') as fp:
        fp.write(pipfile)
    print("Write finish.")


def auto_change():
    systype = platform.system()
    print("System type: " + systype)
    if systype == "Windows":
        path = os.getenv('HOMEPATH') + "\\pip"
        make_dir(path)
        make_file(path + '\\pip.ini')

    elif systype == "Linux" or systype == "Darwin":
        path =os.path.expandvars('$HOME')+"/.pip"
        make_dir(path)
        make_file(path + '/pip.conf')
    else:
        print("System type: " + systype)


if __name__ == "__main__":
    auto_change()
