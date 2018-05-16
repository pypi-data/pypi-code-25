import sys
from argparse import Namespace
from collections import abc
import builtins
from io import TextIOBase
from gettext import gettext
import re
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.tix as tix
import tkinter.scrolledtext as scrolledtext
from types import ModuleType as Module
from typing import List
import yaml
from .helpers import get_back_frame

__all__ = ['load_fp']

wname_regex = re.compile(r'^![a-z]+\d*(.![a-z]+\d*)*$')
call_regex = re.compile(r'^call(/.*)?$')


def load_fp(fp: TextIOBase, master: tk.Misc=None, *,
            use_tix: bool=False, context=None) -> tk.Misc:
    # Default context is the uplevel function locals
    context = context or get_back_frame().f_locals

    if isinstance(context, Namespace):
        # Namespace to dict
        context = context.__dict__
    elif isinstance(context, tuple) and hasattr(context, '_asdict'):
        # Named tuple to dict
        context = context._asdict()

    return load(
        process_values(yaml.load(fp), context=context),
        master=master,
        libs=[tix, tk] if use_tix else [ttk, tk, scrolledtext],
        parent=None,
    )


def load(resource: abc.Mapping, *, master: tk.Misc, libs: List[Module],
         parent: tk.Misc) -> tk.Misc:
    # Type guard
    if len(resource) != 1:
        raise ValueError('multiple widgets: {!r}'.format(resource))

    class_name, settings = next(iter(resource.items()))
    settings = settings or {}
    wclass = get_class(libs, class_name)
    calls = [
        attr for attr in settings.keys()
        if isinstance(getattr(wclass, attr, None), abc.Callable)
        or call_regex.match(attr)
    ]
    kwargs = {
        key: pos_process_values(param, parent=parent)
        for key, param in settings.items()
        if key not in calls and key != 'children'
    }
    widget = wclass(master, **kwargs) if master else wclass(**kwargs)
    parent = parent or widget

    for child in settings.get('children', []):
        load(child, master=widget, libs=libs, parent=parent)

    for attr in calls:
        params=pos_process_values(settings[attr],
                                  current=widget, parent=parent)

        if call_regex.match(attr):
            params[0](*params[1:])
            continue

        method = getattr(widget, attr)

        if attr == 'bind':
            for keysym, callback in params.items():
                method(keysym, callback)

        elif params is None:
            method()

        elif isinstance(params, str):
            method(params)  # required because str is abc.Sequence subclass

        elif isinstance(params, abc.Sequence):
            method(*params)

        elif isinstance(params, abc.Mapping):
            method(**params)

        else:
            method(params)

    return widget


def get_class(libs: List[Module], name: str) -> type:
    name = re.sub(r'[\W_]+', ' ', name).title().replace(' ', '')
    for lib in libs:
        value = getattr(lib, name, None)
        if isinstance(value, type):
            return value
    raise NameError('{} not found in {!r}'.format(name, libs))


def process_values(v, *, context: abc.Mapping={}):
    if isinstance(v, str):
        match = re.match(r'^ctx\[(.+)\]$', v)
        if match:
            key = match.group(1)
            try:
                return context[key]
            except KeyError:
                etype, e, tb = sys.exc_info()
                err = etype(
                    'context has no {}\n{!r}'.format(key, context)
                ).with_traceback(tb)
                err.__context__ = e
                raise err

        match = re.match(r'^_\((.+)\)$', v)
        if match:
            t = context.get('_', getattr(builtins, '_', gettext))
            return t(match.group(1))

        return v

    process = lambda v: process_values(v, context=context)
    if isinstance(v, abc.Sequence):
        return list(map(process, v))

    if isinstance(v, abc.Mapping):
        return {k.replace('-', '_'): process(e) for k, e in v.items()}

    # Fallback to itself
    return v


def pos_process_values(v, *, current: tk.Misc=None, parent: tk.Misc):
    if parent is None:
        return v

    if isinstance(v, str):
        if current and v == '!self':
            return current

        if wname_regex.match(v):
            try:
                return parent.nametowidget(v)
            except KeyError:
                pass

        return v

    process = lambda v: pos_process_values(v, current=current, parent=parent)
    if isinstance(v, abc.Sequence):
        return list(map(process, v))

    if isinstance(v, abc.Mapping):
        return {k.replace('-', '_'): process(e) for k, e in v.items()}

    return v
