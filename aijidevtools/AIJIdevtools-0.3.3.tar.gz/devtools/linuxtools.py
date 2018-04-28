# coding: utf8
from subprocess import Popen, PIPE, DEVNULL
import os
import re
import psutil

from .formtools import tostr
from .exception import mute


__all__ = ['lxrun', 'lxget', 'SPEC']


class Spec:
    # if the specifier is less than zero,
    # then the meth:lxget need no extra argument.
    COMMAND = 2             # COMMAND
    PID = 1
    MANUFACTURER = -1
    OS_VERSION = -2
    PRODUCT_NAME = -3
    SERIAL_NUMBER = -4
    IO_WAIT = -5            # time waiting for I/O completion
    MAC_ADDRESS = -6
    HOSTNAME = -7

    def base(self):
        l = list(filter(lambda x: x[0].isupper()
                        and getattr(self, x) < 0, dir(self)))
        return l


SPEC = Spec()


@mute(not __debug__, '')
def lxget(spec, pid=None, err=False, **kwargs):
    res = ''
    errmsg = ''
    # SWITCH
    if spec == Spec.IO_WAIT:
        foo, errmsg = lxrun('top -b -n 1 | grep wa', err=True)
        p = re.compile(' *([0-9.]*) *wa')
        m = p.search(foo)
        res = m.group(1)

    elif spec == Spec.MANUFACTURER:
        res, errmsg = lxrun("dmidecode -s system-manufacturer", err=True)

    elif spec == Spec.OS_VERSION:
        res, errmsg = lxrun("sed -n '1,1p' /etc/issue", err=True)

    elif spec == Spec.PRODUCT_NAME:
        res, errmsg = lxrun("dmidecode -s system-product-name", err=True)

    elif spec == Spec.SERIAL_NUMBER:
        res, errmsg = lxrun("dmidecode -s system-serial-number", err=True)
        if res == 'Not Specified' or res.startswith('VM'):
            res = ''

    elif spec == Spec.MAC_ADDRESS:
        res, errmsg = lxrun("ifconfig -a", err=True)
        p = ':'.join(['(\w{2})']*6)
        res = ''.join(re.search(p, res).groups())

    elif spec == Spec.HOSTNAME:
        res = lxrun('hostname')

    else:
        pass

    # RETURN
    if err:
        return res, errmsg
    else:
        return res


def lxrun(cmd, err=False, bg=False, daemon=False):
    if isinstance(cmd, list):
        cmd = ' '.join(cmd)

    if bg or daemon:
        p = Popen(cmd, shell=True, stdout=DEVNULL if daemon else None)
        return p

    res = None
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    stdout = tostr(stdout).rstrip()
    stderr = tostr(stderr).rstrip()
    if err:
        return stdout, stderr
    else:
        return stdout


def pyrun(cmd, err=False, daemon=False):
    p = _py3_gen().__next__()
    cmd = ' '.join([p, cmd])
    return lxrun(cmd, err=err, daemon=daemon)


def _py3_gen():
    names = ['python3', 'python'] + ['python3.' + str(i) for i in range(8)]
    p = re.compile('is (/.*python3.*)|is aliased to \'(/.*python3.*)\'')
    for n in names:
        foo, err = lxrun('type ' + n, err=True)
        m = p.search(foo)
        if m:
            yield m.group(1)
