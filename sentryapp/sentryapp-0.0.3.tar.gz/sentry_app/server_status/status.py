#coding: utf8
#author: hepochen@gmail.com
from __future__ import absolute_import
import psutil
from .utils import get_ports_opened, capacity_info_to_dict
from .usage import get_io_usage, get_net_usage, get_processes_usage


def get_system_status(includes_processes=True):
    info = dict()
    cpu_info = dict(
        cores = psutil.cpu_count(),
        logical_cores = psutil.cpu_count(logical=True),
        used = psutil.cpu_percent(interval=1)
    )
    if hasattr(psutil, 'cpu_freq'):
        cpu_freq = psutil.cpu_freq()
        cpu_info['current_freq'] = cpu_freq.current
        cpu_info['max_freq'] = cpu_freq.max
    info['cpu'] = cpu_info

    mem_info = psutil.virtual_memory()
    info['mem'] = capacity_info_to_dict(mem_info)
    info['swap_mem'] = capacity_info_to_dict(psutil.swap_memory())

    try:
        info['disk'] = capacity_info_to_dict(psutil.disk_usage('/etc/hosts')) # for docker, get real disk information
    except:
        info['disk'] = capacity_info_to_dict(psutil.disk_usage('/'))

    info['ports'] = get_ports_opened()

    info['net'] = get_net_usage()

    info['io'] = get_io_usage()

    if includes_processes:
        info['processes'] = get_processes_usage()

    return info

