'''
    Process Manager
    A wrapper of psutil with some useful functions
'''
import re
import warnings
import sys
import signal
from psutil import *

from .linuxtools import lxrun
from .exception import mute


Process.cmd = lambda self: ' '.join(self.cmdline())


@mute(not __debug__, [])
def getpids(pattern, spec='cmd'):
    '''get pids list by command'''
    foo = "ps -eo pid,{0} | \
           grep -v -P '(sudo|grep|PID.*COMMAND)' | \
           grep -P '{1}'".format(spec, pattern)
    foo = lxrun(foo).split('\n')
    
    p = re.compile(' *(\d+)')
    return [int(p.match(i).group(1)) for i in foo if p.match(i)]
    

def kill(pid):
    _, err = lxrun('kill -9 {0}'.format(pid), err=True)
    if err:
        return False
    return True

def kills(cmd):
    res = 0
    for p in getpids(cmd):
        if kill(p):
            res += 1
    return res

# --------Useful wrapper based on psutil------------
def pid_of_listen_port(port): 
    tcps = net_connections(kind='tcp') 
    for conn in tcps:
        if conn.laddr.port == port and conn.status == CONN_LISTEN:
            return conn.pid
    return 0


def kill_proc_tree(p, sig=signal.SIGTERM, include_parent=True,
      timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callabck function which is
    called as soon as a child terminates.
    """
    if isinstance(p, Process):
        pid = p.pid
        parent = p
    else:
        pid = p
        parent = Process(p)
    if pid == os.getpid():
        raise RuntimeError("I refuse to kill myself")
    parent = Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        p.send_signal(sig)
    gone, alive = wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    return (gone, alive)


def reap_children(timeout=3):
    """Tries hard to terminate and ultimately kill all the children of this process.
    This may be useful in unit tests whenever sub-processes are started. 
    This will help ensure that no extra children (zombies) stick around to hog resources.
    """
    def on_terminate(proc):
        print("process {} terminated with exit code {}".format(proc, proc.returncode))

    procs = Process().children()
    # send SIGTERM
    for p in procs:
        p.terminate()
    gone, alive = wait_procs(procs, timeout=timeout, callback=on_terminate)
    if alive:
        # send SIGKILL
        for p in alive:
            print("process {} survived SIGTERM; trying SIGKILL" % p)
            p.kill()
        gone, alive = wait_procs(alive, timeout=timeout, callback=on_terminate)
        if alive:
            # give up
            for p in alive:
                print("process {} survived SIGKILL; giving up" % p)
# --------------------------------------------------



def getpid(cmd=None, pattern=None):
    if cmd is not None:
        foo = getpids(cmd)
        if foo:
            return foo[0]
        return 0

    if pattern is not None:
        pattern = '^.*(:[0-9]{{2}}){{2}} (?!sudo).*{}.*'.format(pattern)
        cmd = "ps -ef | grep -P '{0}'".format(pattern)
        res = lxrun(cmd)
        res = res.strip()
        if not res:
            return 0
        else:
            res = res.split('\n')
            res = filter(lambda x: 'grep' not in x, res)
            res = list(res)
            pid = re.split(' +', res[0])[1]
            return int(pid)

def getports(command=''):
    return get_port_names(command).keys()

def get_port_names(command='', pid=-1):
    '''get tcp listening port and names'''
    foo = lxrun("netstat -plnt")
    foo = foo.split('\n')
    
    p = 'tcp +\d+ +\d+ +[^ ]*:(\d+) .+' + \
        (str(pid) if pid>=0 else '\d+') + '/' + \
        '([^ ]*{0}[^ ]*)'.format(command)

    p = re.compile(p)
    res = {}
    for i in foo:
        m = p.match(i)
        if m:
            k, v= m.groups()
            if re.search(command, v):
                k = int(k)
                res[k] = v.strip()
    return res


def reboot(pid):
    cmd = get_command(pid)
    kill(pid)
    lxrun(cmd, daemon=True)
    pid = get_pid(pattern=cmd)
    return pid


# ----------------- Full tested internal function  -----------------------


# Old version API
def getcmd(pid):
    warnings.warn("pm.getcmd(pid) will be deleted in the futur.\nUse pm.get(pid, 'cmd') instead.", DeprecationWarning)
    print(sys._getframe().f_back.f_globals['__file__'], ': line ', sys._getframe().f_back.f_lineno)
    return get(pid, 'cmd')

