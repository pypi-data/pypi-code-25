# cam - C/C++ Archive Manager Open Source software
#

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import os.path
import functools
import getpass
import sys
import argparse
import warnings
import shlex
import subprocess
import colorama
from colorama import init

Fore  = colorama.Fore
Back  = colorama.Back
Style = colorama.Style

import cam
from cam.sysinfo import PLATFORM,ARCH
from cam.enums import Platform,Architecture
from cam.errors import FatalError
_colorama_stream = None

if PLATFORM == Platform.WINDOWS:
    colorama.init( wrap = False )
    _colorama_stream = colorama.AnsiToWin32(sys.stderr).stream

else:
    colorama.init(autoreset = True)


# Shim for raw_input,print in python3
if sys.version_info > (3,):
    input_func = input
else:
    input_func = raw_input

class Capturer(object):

    def __init__(self):
        self.records = None

    def open(self,cmd = True, log = False):
        self.records =[]
        self.record_cmd = cmd
        self.record_log = log

    def close(self):
        self.records =None
        self.record_cmd = False
        self.record_log = False

    def reset(self):
        if self.records:
            self.records =[]

    def calls(self):
        l=[]
        for items in self.records:
            if items.get('type',None) == 'call':
                l.append(items.get('cmd'))
        return l
    
    def logs(self):
        pass
    


capturer = Capturer()

def log(*args):
    if capturer.records is not None:
        if capturer.record_log:
            capturer.records.append({'type':'log',
            'msg': args   })
        return
    for arg in args:
        print(arg, file= _colorama_stream,end='')

    if _colorama_stream:
        print(Style.RESET_ALL,file=_colorama_stream )


class OStream:
    ''' out stream
    '''

    def __init__(self, stream=sys.stdout):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)
       
#def Call(cmd, cmd_dir='.',stream = sys.stdout):
#    if capturer.records is not None:
#        if capturer.record_cmd:
#            capturer.records.append({'type':'call',
#            'cmd': cmd,
#            'cwd': os.path.abspath(cmd_dir)   })
#        return
#
#    
#    if stream.stream != sys.stdout:
#        stream.write("Running command '%s'\n" % cmd)
#        stream.flush()
#    
#    subprocess.check_call(cmd, cwd=cmd_dir,
#        stderr= subprocess.STDOUT,
#        stdout= stream,
#        env=os.environ.copy(), shell=True)

stdout = sys.stdout

def call(cmd, cmd_dir='.',stream = None, fail=True):
    '''
    Run a shell command

    @param cmd: the command to run
    @type cmd: str
    @param cmd_dir: directory where the command will be run
    @param cmd_dir: str
    @param fail: whether or not to raise an exception if the command fails
    @type fail: bool
    '''
    if capturer.records is not None:
        if capturer.record_cmd:
            capturer.records.append({'type':'call',
            'cmd': cmd,
            'cwd': os.path.abspath(cmd_dir)   })
        return

    global stdout
    if stdout is None:
        stdout = sys.stdout

    if stream is None:
        stream = stdout
        
    
    if stream != sys.stdout:
        stream.write("Running command '%s'\n" % cmd)
        stream.flush()

    ret = 0
    try:
        subprocess.check_call(cmd, cwd=cmd_dir,
        stderr= subprocess.STDOUT,
        stdout= stream,
        env=os.environ.copy(), shell=True)

    except subprocess.CalledProcessError:
        if fail:
            raise FatalError("Error running command: %s"% cmd)
        else:
            ret = 0
    return ret


def check_call(cmd, cmd_dir=None, fail=False):
    if capturer.records is not None:
        if capturer.record_cmd:
            capturer.records.append({'type':'call',
            'cmd': cmd,
            'cwd': os.path.abspath(cmd_dir)   })
            return

    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    try:
        process = subprocess.Popen(cmd, cwd=cmd_dir,
                                   stdout=subprocess.PIPE,
                                   stderr=open(os.devnull), shell=True)
        output, unused_err = process.communicate()
        if process.poll() and fail:
            raise Exception()
    except Exception:
        raise FatalError("Error running command: %s"% cmd)

    if sys.stdout.encoding:
        output = output.decode(sys.stdout.encoding)

    return output