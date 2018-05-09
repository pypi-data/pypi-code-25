import inspect
import os.path as path
import tkinter as tk
from typing import Callable


def fixtures(
    origin: str = None
) -> Callable[[str, tk.Misc, bool, object], tk.Misc]:
    if origin is None:
        ref = get_back_frame().f_code.co_filename
        origin = path.realpath(
            path.join(path.dirname(ref), 'fixtures')
        )

    def load(fixture: str, master: tk.Misc, *,
             use_tix: bool=False, context=None) -> tk.Misc:
        context = context or get_back_frame().f_locals
        from .loader import load_fp
        with open(path.join(origin, fixture)) as fp:
            return load_fp(fp, master, use_tix=use_tix, context=context)

    return load


def get_back_frame():
    return inspect.currentframe().f_back.f_back
