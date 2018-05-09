from argparse import Namespace
from functools import partial
from io import TextIOBase
import re
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.tix as tix
import tkinter.scrolledtext as scrolledtext
from typing import Any, Generator, Tuple
import yaml

__all__ = ['load_file']


def load_fp(fp: TextIOBase, master: tk.Misc, *,
            use_tix: bool=False, context=None) -> tk.Misc:
    if context is None:
        # Default context is the uplevel function locals
        import inspect
        frame = inspect.currentframe()
        context = frame.f_back.f_locals # get from top frame
    if isinstance(context, Namespace):
        # Namespace to dict
        context = context.__dict__
    elif isinstance(context, tuple) and hasattr(context, '_asdict'):
        # Named tuple to dict
        context = context._asdict()

    return load(yaml.load(fp), master, use_tix, context, is_root=True)


def load(resource: dict, master: tk.Misc, use_tix: bool, context: dict,
         is_root: bool=False) -> tk.Misc:
    libs = [tix] if use_tix else[ttk, tk, scrolledtext]
    iterit = partial(iter_resource, context)

    for k, v in iterit(resource):
        # The bind key can be used to bind key events to handles.
        if k == 'bind':
            for key, value in iterit(v):
                master.bind(key, value)

        # It considers call/* as method calls
        elif k.startswith('call/'):
            k = k.split('/')[1]
            if isinstance(v, list):
                getattr(master, k)(*v)
            elif isinstance(v, dict):
                getattr(master, k)(**v)
            elif v is None:
                getattr(master, k)()
            else:
                getattr(master, k)(v)

        # If v is a dict, this assumes it represents inner widgets(s)
        elif isinstance(v, dict):
            k = re.sub(r'[\W_]+', ' ', k).title().replace(' ', '')
            for lib in libs:
                if hasattr(lib, k):
                    w = load(v, getattr(lib, k)(master), use_tix, context)
                    if is_root:
                        return w
                    break
            else:
                raise KeyError('key "{}" not found'.format(k))

        # Anything else is a tk widget parameter
        else:
            # Some parameters are attributes
            if hasattr(master, k):
                setattr(master, k, v)

            # Other are map keys
            else:
                master[k] = v

    return master


def iter_resource(context: dict, resource: dict
                  ) -> Generator[Tuple[str, Any], None, None]:
    """
    Returns each key-value pair in the resource, considering context keys if
    the value is in the format ctx[name]
    """
    for k, v in resource.items():
        # Known geometry managers
        if k in 'grid pack place'.split():
            k = 'call/{}'.format(k)
        yield k, get_ctx_value(context, v)


def get_ctx_value(context: dict, value: str):
    """
    Extracts ctx[key] to content of key in the context, or value itself if the
    key does not exist or the value does not match the pattern.
    """
    if not isinstance(value, str):
        return value
    match = re.match(r'ctx\[(.+)\]', value)
    return context[match.group(1)] if match else value
