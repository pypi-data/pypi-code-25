#!/usr/bin/env python
import os
import time
from string import Formatter
import shlex
import click
import psutil


ALL_ATTRIBUTES = set([name for name in dir(psutil.Process) if not name.startswith("_")])
IGNORE_ATTRIBUTES = set([
    "as_dict",
    "children",
    "is_running",
    "kill",
    "oneshot",
    "parent",
    "resume",
    "send_signal",
    "suspend",
    "terminal",
    "terminate",
    "wait",
])
AVAILABLE_ATTRIBUTES = sorted(list(ALL_ATTRIBUTES - IGNORE_ATTRIBUTES) + ["elapsed_time"])
AVAILABLE_ATTRIBUTES_STRING = "\n".join(AVAILABLE_ATTRIBUTES)


def cast(value):
    if hasattr(value, "_asdict"):
        return dict(value._asdict())
    return value


def get_process_attribute(process, name):
    if name == "elapsed_time":
        return time.time() - process.create_time()
    if name == "nice":
        value = process.nice()
        if isinstance(value, (int, float)):
            return {"name": "NICE", "value": value}
        else:
            return {"name": value.name, "value": value.value}
    if hasattr(process, name):
        value = getattr(process, name)
        if callable(value):
            value = value()
        if name == "cmdline":
            return " ".join(shlex.quote(arg) for arg in value)
        if isinstance(value, (str, int, float, bool, dict)):
            return value
        if isinstance(value, (set, list)):
            return [cast(x) for x in value]
        return cast(value)
    else:
        return None


def get_process_info(process, keys):
    info = {}
    for key in keys:
        info[key] = get_process_attribute(process, key)
    return info


class Object(object):
    def __repr__(self):
        return str(self.__dict__)


def format_object_cast(value):
    if isinstance(value, (set, list)):
        result = Object()
        for index in range(len(value)):
            setattr(result, str(index), format_object_cast(value[index]))
        return result
    if isinstance(value, dict):
        result = Object()
        keys = list(value.keys())
        for key in keys:
            setattr(result, key, format_object_cast(value[key]))
        return result
    return value


def print_process_line(process, output):
    keys = set([fn.split(".")[0] for _, fn, _, _ in Formatter().parse(output) if fn is not None])
    info = get_process_info(process, keys)
    info2 = {}
    for key, value in info.items():
        info2[key] = format_object_cast(value)
    line = output.format(**info2)
    click.echo(line)


@click.command()
@click.argument("output", required=False)
def main(output):
    """Show all processes with output template.

    The keywords can be used in output template are:

    cmdline
    connections
    cpu_percent
    cpu_times
    create_time
    cwd
    elapsed_time
    environ
    exe
    gids
    memory_full_info
    memory_info
    memory_info_ex
    memory_maps
    memory_percent
    name
    nice
    num_ctx_switches
    num_fds
    num_threads
    open_files
    pid
    ppid
    status
    threads
    uids
    username


    The default output template is: "{pid}\\t{name}"
    """
    if output is None:
        output = "{pid}\t{name}"
    else:
        output = eval('"'+output+'"')
    for process in psutil.process_iter():
        try:
            print_process_line(process, output)
        except:
            pass

if __name__ == "__main__":
    main()
