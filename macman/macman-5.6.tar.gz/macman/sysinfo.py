#!/usr/bin/python
# Filename: sysinfo.py

from subprocess import Popen, PIPE
import macman

def getSerialNumber():
    """ Retrieve serial number of OSX/macOS machine """

    args = ["ioreg -l | awk '/IOPlatformSerialNumber/ {print $4;}'"]
    p = Popen(args, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = p.communicate()
    return output.strip()[1:-1]


def getModel():
    """ Retrieve model of OSX/macOS machine """

    args = ["ioreg -c IOPlatformExpertDevice -d 2 | awk '/model/ {print $3}'"]
    p = Popen(args, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = p.communicate()
    return output.strip()[2:-2]
