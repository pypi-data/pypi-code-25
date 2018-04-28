from __future__ import absolute_import
import sys
import time
import os
import errno
import shlex
import pydoc
import inspect
import collections
from io import open
from itertools import izip

color2num = dict(
    gray=30,
    red=31,
    green=32,
    yellow=33,
    blue=34,
    magenta=35,
    cyan=36,
    white=37,
    crimson=38
)


def colorize(string, color, bold=False, highlight=False):
    attr = []
    num = color2num[color]
    if highlight:
        num += 10
    attr.append(unicode(num))
    if bold:
        attr.append(u'1')
    return u'\x1b[%sm%s\x1b[0m' % (u';'.join(attr), string)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def log(s):  # , send_telegram=False):
    print s
    sys.stdout.flush()


class SimpleMessage(object):

    def __init__(self, msg, logger=log):
        self.msg = msg
        self.logger = logger

    def __enter__(self):
        print self.msg
        self.tstart = time.time()

    def __exit__(self, etype, *args):
        maybe_exc = u"" if etype is None else u" (with exception)"
        self.logger(u"done%s in %.3f seconds" %
                    (maybe_exc, time.time() - self.tstart))


MESSAGE_DEPTH = 0


class Message(object):

    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        global MESSAGE_DEPTH  # pylint: disable=W0603
        print colorize(u'\t' * MESSAGE_DEPTH + u'=: ' + self.msg, u'magenta')
        self.tstart = time.time()
        MESSAGE_DEPTH += 1

    def __exit__(self, etype, *args):
        global MESSAGE_DEPTH  # pylint: disable=W0603
        MESSAGE_DEPTH -= 1
        maybe_exc = u"" if etype is None else u" (with exception)"
        print colorize(u'\t' * MESSAGE_DEPTH + u"done%s in %.3f seconds" % (maybe_exc, time.time() - self.tstart), u'magenta')


def prefix_log(prefix, logger=log):
    return lambda s: logger(prefix + s)


def tee_log(file_name):
    f = open(file_name, u'w+')

    def logger(s):
        log(s)
        f.write(s)
        f.write(u'\n')
        f.flush()
    return logger


def collect_args():
    splitted = shlex.split(u' '.join(sys.argv[1:]))
    return dict((arg_name[2:], arg_val)
            for arg_name, arg_val in izip(splitted[::2], splitted[1::2]))


def type_hint(arg_name, arg_type):
    def wrap(f):
        meta = getattr(f, u'__tweak_type_hint_meta__', None)
        if meta is None:
            f.__tweak_type_hint_meta__ = meta = {}
        meta[arg_name] = arg_type
        return f
    return wrap


def tweak(fun_or_val, identifier=None):
    if isinstance(fun_or_val, collections.Callable):
        return tweakfun(fun_or_val, identifier)
    return tweakval(fun_or_val, identifier)


def tweakval(val, identifier):
    if not identifier:
        raise ValueError(u'Must provide an identifier for tweakval to work')
    args = collect_args()
    for k, v in args.items():
        stripped = k.replace(u'-', u'_')
        if stripped == identifier:
            log(u'replacing %s in %s with %s' % (stripped, unicode(val), unicode(v)))
            return type(val)(v)
    return val


def tweakfun(fun, alt=None):
    u"""Make the arguments (or the function itself) tweakable from command line.
    See tests/test_misc_console.py for examples.

    NOTE: this only works for the initial launched process, since other processes
    will get different argv. What this means is that tweak() calls wrapped in a function
    to be invoked in a child process might not behave properly.
    """
    cls = getattr(fun, u'im_class', None)
    method_name = fun.__name__
    if alt:
        cmd_prefix = alt
    elif cls:
        cmd_prefix = cls + u'.' + method_name
    else:
        cmd_prefix = method_name
    cmd_prefix = cmd_prefix.lower()
    args = collect_args()
    if cmd_prefix in args:
        fun = pydoc.locate(args[cmd_prefix])
    if type(fun) == type:
        argspec = inspect.getargspec(fun.__init__)
    else:
        argspec = inspect.getargspec(fun)
    # TODO handle list arguments
    defaults = dict(
        list(izip(argspec.args[-len(argspec.defaults or []):], argspec.defaults or [])))
    replaced_kwargs = {}
    cmd_prefix += u'-'
    if type(fun) == type:
        meta = getattr(fun.__init__, u'__tweak_type_hint_meta__', {})
    else:
        meta = getattr(fun, u'__tweak_type_hint_meta__', {})
    for k, v in args.items():
        if k.startswith(cmd_prefix):
            stripped = k[len(cmd_prefix):].replace(u'-', u'_')
            if stripped in meta:
                log(u'replacing %s in %s with %s' % (stripped, unicode(fun), unicode(v)))
                replaced_kwargs[stripped] = meta[stripped](v)
            elif stripped not in argspec.args:
                raise ValueError(
                    u'%s is not an explicit parameter of %s' % (stripped, unicode(fun)))
            elif stripped not in defaults:
                raise ValueError(
                    u'%s does not have a default value in method %s' % (stripped, unicode(fun)))
            elif defaults[stripped] is None:
                raise ValueError(
                    u'Cannot infer type of %s in method %s from None value' % (stripped, unicode(fun)))
            else:
                log(u'replacing %s in %s with %s' % (stripped, unicode(fun), unicode(v)))
                # TODO more proper conversions
                replaced_kwargs[stripped] = type(defaults[stripped])(v)

    def tweaked(*args, **kwargs):
        all_kw = dict(list(izip(argspec[0], args)) +
                      list(kwargs.items()) + list(replaced_kwargs.items()))
        return fun(**all_kw)
    return tweaked


def query_yes_no(question, default=u"yes"):
    u"""Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {u"yes": True, u"y": True, u"ye": True,
             u"no": False, u"n": False}
    if default is None:
        prompt = u" [y/n] "
    elif default == u"yes":
        prompt = u" [Y/n] "
    elif default == u"no":
        prompt = u" [y/N] "
    else:
        raise ValueError(u"invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == u'':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(u"Please respond with 'yes' or 'no' "
                             u"(or 'y' or 'n').\n")
