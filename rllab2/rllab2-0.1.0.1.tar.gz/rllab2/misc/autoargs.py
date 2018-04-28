from __future__ import absolute_import
from rllab2.misc.console import colorize
import inspect
from itertools import izip


# pylint: disable=redefined-builtin
# pylint: disable=protected-access
def arg(name, type=None, help=None, nargs=None, mapper=None, choices=None,
        prefix=True):
    def wrap(fn):
        assert fn.__name__ == u'__init__'
        if not hasattr(fn, u'_autoargs_info'):
            fn._autoargs_info = dict()
        fn._autoargs_info[name] = dict(
            type=type,
            help=help,
            nargs=nargs,
            choices=choices,
            mapper=mapper,
        )
        return fn
    return wrap


def prefix(prefix_):
    def wrap(fn):
        assert fn.__name__ == u'__init__'
        fn._autoargs_prefix = prefix_
        return fn
    return wrap


def _get_prefix(cls):
    from rllab2.mdp.base import MDP
    from rllab2.policies.base import Policy
    from rllab2.baselines.base import Baseline
    from rllab2.algos.base import Algorithm

    if hasattr(cls.__init__, u'_autoargs_prefix'):
        return cls.__init__._autoargs_prefix
    elif issubclass(cls, MDP):
        return u'mdp_'
    elif issubclass(cls, Algorithm):
        return u'algo_'
    elif issubclass(cls, Baseline):
        return u'baseline_'
    elif issubclass(cls, Policy):
        return u'policy_'
    else:
        return u""


def _get_info(cls_or_fn):
    if isinstance(cls_or_fn, type):
        if hasattr(cls_or_fn.__init__, u'_autoargs_info'):
            return cls_or_fn.__init__._autoargs_info
        return {}
    else:
        if hasattr(cls_or_fn, u'_autoargs_info'):
            return cls_or_fn._autoargs_info
        return {}


def _t_or_f(s):
    ua = unicode(s).upper()
    if ua == u'TRUE'[:len(ua)]:
        return True
    elif ua == u'FALSE'[:len(ua)]:
        return False
    else:
        raise ValueError(u'Unrecognized boolean value: %s' % s)


def add_args(_):
    def _add_args(cls, parser):
        args_info = _get_info(cls)
        prefix_ = _get_prefix(cls)
        for arg_name, arg_info in args_info.items():
            type = arg_info[u'type']
            # unfortunately boolean type doesn't work
            if type == bool:
                type = _t_or_f
            parser.add_argument(
                u'--' + prefix_ + arg_name,
                help=arg_info[u'help'],
                choices=arg_info[u'choices'],
                type=type,
                nargs=arg_info[u'nargs'])
    return _add_args


def new_from_args(_):
    def _new_from_args(cls, parsed_args, *args, **params):
        silent = params.pop(u"_silent", False)
        args_info = _get_info(cls)
        prefix_ = _get_prefix(cls)
        #     params = dict()
        for arg_name, arg_info in args_info.items():
            prefixed_arg_name = prefix_ + arg_name
            if hasattr(parsed_args, prefixed_arg_name):
                val = getattr(parsed_args, prefixed_arg_name)
                if val is not None:
                    if arg_info[u'mapper']:
                        params[arg_name] = arg_info[u'mapper'](val)
                    else:
                        params[arg_name] = val
                    if not silent:
                        print colorize(
                            u"using argument %s with value %s" % (arg_name, val),
                            u"yellow")
        return cls(*args, **params)
    return _new_from_args


def inherit(base_func):
    assert base_func.__name__ == u'__init__'

    def wrap(func):
        assert func.__name__ == u'__init__'
        func._autoargs_info = dict(
            _get_info(base_func),
            **_get_info(func)
        )
        return func
    return wrap


def get_all_parameters(cls, parsed_args):
    prefix = _get_prefix(cls)
    if prefix is None or len(prefix) == 0:
        raise ValueError(u'Cannot retrieve parameters without prefix')
    info = _get_info(cls)
    if inspect.ismethod(cls.__init__):
        spec = inspect.getargspec(cls.__init__)
        if spec.defaults is None:
            arg_defaults = {}
        else:
            arg_defaults = dict(list(izip(spec.args[::-1], spec.defaults[::-1])))
    else:
        arg_defaults = {}
    all_params = {}
    for arg_name, arg_info in info.items():
        prefixed_name = prefix + arg_name
        arg_value = None
        if hasattr(parsed_args, prefixed_name):
            arg_value = getattr(parsed_args, prefixed_name)
        if arg_value is None and arg_name in arg_defaults:
            arg_value = arg_defaults[arg_name]
        if arg_value is not None:
            all_params[arg_name] = arg_value
    return all_params
