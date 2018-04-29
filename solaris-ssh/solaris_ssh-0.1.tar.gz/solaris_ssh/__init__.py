#!/usr/bin/python3.6

'''
Written by Nick Chesser(d861854) - 13/04/2018
Python Helper functions for SSH, SCP etc
Requires ssh keys to be setup, in order to function

SSHConnect - Connect to host and run commands 
ParallelSSH - Allows ssh execution in parallel on multiple hosts

Current Functionality:
- Run commands over ssh
- Load commands from file
- Save output to file
- Run sudo on Linux Servers
- Custom function support for manipulating data with ParallelSSH

TODOs:
- Add SCP, SFTP functionallity
- 

Examples can be found here - /data/scripts/python_functions/python_ssh_examples.py
'''

import os
import json
import pickle
import subprocess
import getpass

from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
SSH = ('ssh', '-T', '-o', 'LogLevel=ERROR', '-o', 'ConnectTimeout=6',
       '-o', 'PreferredAuthentications=publickey', '-o', 'BatchMode=yes',
       '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectionAttempts=3')

# Required to run sudo on linux boxes
SUDO_SSH = ('ssh', '-tt', '-o', 'LogLevel=ERROR', '-o', 'ConnectTimeout=6',
       '-o', 'PreferredAuthentications=publickey', '-o', 'BatchMode=yes',
       '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectionAttempts=3')


# General Utility functions
def check_isfile(filename):
    isfile = os.path.isfile(filename)
    if not isfile: print(filename + ' is not a valid file')
    return isfile

def save_output_to_file(filename, outputs):
    # Perhaps save in the current folder the script is running
    print(outputs.items())
    with open(filename, 'wb') as file:
        pass

    print('Output saved to ' + filename) 

# Functions for SCP
def get_hosts(hostfile):
    with open(hostfile, 'r') as file:
        hosts = file.read().splitlines()
    return hosts


def get_files(filesfile):
    with open(filesfile, 'r') as file:
        files = file.read().splitlines()
    return set(file for file in files if check_isfile(file))


def run_subprocess(commands):
    results = subprocess.Popen([*commands],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return results


def run_ssh(host, commands, timeout=None):
    # run ssh command and functions
    ssh = subprocess.Popen([*SSH, host, commands],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

    # if timeout is set, kill processes that are taking too long
    try:
        outs, errs = ssh.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        ssh.kill()
        outs, errs = ssh.communicate()

    return host, {'outs': outs, 'errs': errs}


# Run ssh connections across multiple hosts
class ParallelSSH():
    def __init__(self, hosts: list, use_stdout=True, infile=None, pcons=4, cust_func=None, save_output=False):
        self._hosts = hosts
        self._use_stdout = use_stdout
        self._pcons = pcons
        self._cust_func = cust_func
        self._save_output = save_output 

        self._outputs = {}


    def run_parallel_ssh(self, commands, timeout=None):
        with ThreadPoolExecutor(max_workers=self._pcons) as executor:
            results = {executor.submit(run_ssh, host, commands) for host in self._hosts}

            for future in as_completed(results):
                try:
                    host, data = future.result()
                except Exception as exc:
                    print('Failed')
                else:
                    self._outputs[host] = data
                    if self._cust_func:
                        self._cust_func(data)

        print('Finished running in parallel')
        if self._save_output:
            save_output_to_file('parrallel_output.txt', self._outputs)


    @property
    def outputs(self) -> dict:
        return self._outputs
    


# SCP files to hosts
class SCP:
    def __init__(self, hosts, files):
        self._hosts = hosts
        self._files = files


    # load hosts and files to send from files
    @classmethod
    def hf(cls, hosts_file, files_file):
        cls._hosts = get_hosts(hosts_file)
        cls._files = get_files(files_file)
        return cls(cls._hosts, cls._files)


     # upload file to remote host
    def put(self, files):
        if type(files) == str:
            files = [files]

        valid_files = [file for file in files if check_isfile(file)]

        if len(valid_files) < 1:
            return print('No valid files inputed')

        if type(self._hosts) == str:
            self._hosts = [self._hosts]

        for host in self._hosts:
            scp = run_subprocess(['scp', *files, host + ':'])

        print('SCP transfer complete to - ' + str(self._hosts))


    # get a file from remote host
    def get(self, files):
        pass


def main():
    ssh = ParallelSSH(['localhost', '192.168.2.186'])
    ssh.run_parallel_ssh('uname -a')
    print(ssh.outputs)
    

if __name__ == "__main__":
    main()
