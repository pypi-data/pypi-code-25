# Copyright (c) 2014 ETH Zurich, Institute of Astronomy, Lukas Gamper <lukas.gamper@usystems.ch>

from __future__ import print_function, division, absolute_import, unicode_literals


import os
import sys
import hashlib
import inspect
import warnings

from hope._wrapper import Wrapper
import hope._cache as cache
from hope import config
from hope import serialization
from hope._wrapper import get_config_attrs
from hope._wrapper import get_fkt_hash


IS_PY_2 = (sys.version_info[0] == 2)


def jit(fkt):
    """
    Compiles a function to native code and return the optimized function. The new function has the
    performance of a compiled function written in C.

    :param fkt: function to compile to c
    :type fkt: function
    :returns: function -- optimized function

    This function can either be used as decorator

    .. code-block:: python

        @jit
        def sum(x, y):
            return x + y

    or as a normal function

    .. code-block:: python

        def sum(x, y):
            return x + y
        sum_opt = jit(sum)
    """

    if config.hopeless:
        return fkt

    argspec = inspect.getargspec(fkt) if IS_PY_2 else inspect.getfullargspec(fkt)
    # the gettattr fixes differences between getfullargspec and getargspec(python<3.6):
    if argspec.varargs is not None or getattr(argspec, "keywords", argspec.varkw) is not None:
        raise ValueError("Jitted functions should not have *args or **kwargs")

    hash_ = hashlib.sha224(inspect.getsource(fkt).encode('utf-8')).hexdigest()
    filename = "{0}_{1}".format(fkt.__name__, hash_)

    if not os.path.exists(config.prefix):
        os.makedirs(config.prefix)

    if config.prefix not in sys.path:
        sys.path.append(os.path.abspath(config.prefix))

    wrapper = Wrapper(fkt, hash_)

    try:
        state = serialization.unserialize(filename)
        if state is not None:
            _check_state(fkt, state)
        else:
            raise ImportError("No state found.")

        if sys.version_info[0] == 2:
            module = __import__(state["filename"], globals(), locals(), [], -1)
        else:
            import importlib
            module = importlib.import_module(state["filename"])

        if "bound" in state and state["bound"]:
            def _hope_callback(*args):
                return module.run(*args)
            setattr(cache, str(id(_hope_callback)), fkt)
            return _hope_callback

        module.set_create_signature(wrapper.create_signature)
        setattr(cache, str(id(module.run)), fkt)
        return module.run

    except LookupError as le:
        if config.verbose:
            warnings.warn("Recompiling... Reason: {0}".format(le))
        wrapper._recompile = True
        return wrapper.callback
    except ImportError:
        return wrapper.callback


def _check_state(fkt, state):
    for name in get_config_attrs():
        if name not in state or state[name] != getattr(config, name):
            msg = "State is inconsistent with config. Inconsistent state key: [{0}].".format(name)
            raise LookupError(msg)

    if "main" not in state or "called" not in state or state["main"] != fkt.__name__:
        raise LookupError("State is inconsistent")

    for name, value in list((state["called"] if "called" in state else {}).items()):
        if name not in fkt.__globals__:
            msg = ("State is inconsistent. "
                   "Called function '%s' cannot be found in %s's global scope." % (name,
                                                                                   fkt.__name__))
            raise LookupError(msg)

        glob_fkt = fkt.__globals__[name]
        if isinstance(glob_fkt, Wrapper):
            if "filename" in state and get_fkt_hash(glob_fkt.fkt) != value:
                raise LookupError("State is inconsistent. Hash(sha224) has changed")
        elif inspect.isbuiltin(glob_fkt) and hasattr(cache, str(id(glob_fkt))):
            if "filename" in state and get_fkt_hash(getattr(cache, str(id(glob_fkt)))) != value:
                raise LookupError("State is inconsistent. Hash(sha224) has changed")
        elif inspect.isfunction(glob_fkt):
            if "filename" in state and get_fkt_hash(glob_fkt) != value:
                raise LookupError("State is inconsistent. "
                                  "Hash(sha224) of called function '%s' has changed" % name)
        elif "filename" in state:
            raise LookupError("State is inconsistent.")
