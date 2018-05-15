import pathlib, os
from pathlib import Path

def unlink_f(path):
    if Path(path).is_file():
        os.unlink(path)

def link_f(src, target):
    target = Path(target)
    if target.is_file():
        os.unlink(target)
    os.link(src, target)