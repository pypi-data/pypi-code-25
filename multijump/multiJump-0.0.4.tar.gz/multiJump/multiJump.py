#! /usr/bin/env python3
# coding=utf-8
import sys
import paramiko
import socket
import time 

class ParaProxy(paramiko.util.ClosingContextManager):  
    """  
    Instead of ProxyCommand.  
    Solving ProxyCommand cannot connect to machine with password.  
    """  
    def __init__(self, stdin, stdout, stderr):  
        self.stdin = stdin  
        self.stdout = stdout  
        self.stderr = stderr  
        self.timeout = None  
  
    def send(self, content):  
        try:  
            self.stdin.write(content)  
        except IOError as exc:  
            print('IOError exception.')  
            return  
        return len(content)  
  
    def recv(self, size):  
        buffer = b''  
        start = time.time()  
        while len(buffer) < size:  
            if self.timeout is not None:  
                elapsed = (time.time() - start)  
                if elapsed >= self.timeout:  
                    raise socket.timeout()  
            buffer += self.stdout.read(size - len(buffer))  
        return buffer  
  
    def close(self):  
        self.stdin.close()  
        self.stdout.close()  
        self.stderr.close()  

    def _closed(self):  
        self.stdin.close()  
        self.stdout.close()  
        self.stderr.close()  
  
    def settimeout(self, timeout):  
        self.timeout = timeout

class jump_exe_cmd:
    def __init__(self, mid_host_ip = None, mid_port=22, mid_username=None, mid_password=None, mid_connect_timeout=60 , cmd_mid = None, end_host_ip = None, end_port = None, cmd_end_to_exe = None, end_host_user = None): 
        self.mid_host_ip = mid_host_ip
        self.mid_port = mid_port
        self.mid_username = mid_username
        self.mid_password = mid_password
        self.mid_connect_timeout = mid_connect_timeout
        self.cmd_mid = cmd_mid
        self.end_host_ip = end_host_ip
        self.end_port = end_port
        self.cmd_end_to_exe = cmd_end_to_exe
        self.end_host_user = end_host_user

    def exe_cmd(self):
        mid_cli = paramiko.SSHClient()  
        mid_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
        mid_cli.connect(hostname=self.mid_host_ip, port=self.mid_port, username=self.mid_username, password=self.mid_password, timeout=self.mid_connect_timeout)
        print ('Connect to %s successfully !' % self.mid_host_ip)

        if self.cmd_mid:  
            stdin, stdout, stderr = mid_cli.exec_command(self.cmd_mid)  
            print('stdout %s' % (''.join(stdout.readlines())))  
            error_msg = ''.join(stderr.readlines())
            if error_msg != '':  
                raise paramiko.ssh_exception(error_msg)  
            else:  
                print ('run cmd %s on %s successfully!' % (self.cmd_mid, self.mid_host_ip))  
            stderr.close()  
            stdout.close()  

        io_tupple = mid_cli.exec_command('nc %s %s' % (self.end_host_ip, self.end_port))

        proxy = ParaProxy(*io_tupple)  
        proxy.settimeout(1000)  

        # Connecting to AnotherMachine and executing... anything...  
        end_cli = paramiko.SSHClient()  
        end_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
        #end_cli.connect(hostname=end_host_ip, username=end_host_user,password=end_host_password, sock=proxy) 
        end_cli.connect(hostname=self.end_host_ip, username=self.end_host_user, sock=proxy)

        print ('Connect to %s successfully !' % self.end_host_ip)  
        print ('run end_cmd .......')  
        stdin, stdout, stderr = end_cli.exec_command(self.cmd_end_to_exe)  
        print ('run end_cmd successfully')

        # waiting for exit status (that means cmd finished)  
        exit_status = stdout.channel.recv_exit_status()  

        end_cli.close()  
        mid_cli.close()  
