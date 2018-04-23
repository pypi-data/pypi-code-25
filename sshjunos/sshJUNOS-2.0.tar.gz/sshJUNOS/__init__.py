#!/usr/bin/env python3
from __future__ import print_function
import sys, socket, getpass
from netmiko import ConnectHandler, NetMikoAuthenticationException

def sshHost(hostname):
    '''Juniper ssh module based on netmiko. Example: "python3 sshHostModuleJUNOS.py mydevice.lab"'''
    try:
        username = raw_input("Username: ")
    except NameError:
        username = input("Username: ")
    finally:
        password = getpass.getpass()
        hostIp = socket.gethostbyname(hostname)
    try:
        sshSession = ConnectHandler(device_type='juniper', ip=hostIp, username=username, password=password)
    except NetMikoAuthenticationException:
        print('Authentication failed! Please retry')
        sys.exit(1)
    except ValueError:
        print('Enable password wrong! Please retry')
        sys.exit(1)
    else:
        versionHostname = sshSession.send_command("show version | match Hostname:")
        print('Session established with Hostname: {} IP: {}'.format(versionHostname.strip(), hostIp))
        return sshSession

if __name__ == "__main__":
    try:
        sshHost(sys.argv[1])
    except IndexError:
        print('Please, specify hostname device. Example: "python3 sshHostModuleJUNOS.py mydevice.lab"')
