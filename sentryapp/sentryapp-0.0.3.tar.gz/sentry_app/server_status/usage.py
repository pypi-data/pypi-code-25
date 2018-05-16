#coding: utf8
#author: hepochen@gmail.com
from __future__ import absolute_import
import psutil, time
from .utils import bytes2human
from .process_status import get_processes_raw_data


def get_diff_value(current, pre, field):
    if hasattr(current, field):
        current_value = getattr(current, field)
    else:
        current_value = current.get(field)
    if hasattr(pre, field):
        pre_value = getattr(pre, field)
    else:
        pre_value = pre.get(field)
    if pre_value is not None and current_value is not None:
        return current_value-pre_value
    else:
        return 0


class Usage(object):
    def __init__(self, raw_data_get_func):
        self.prev = None
        self.prev_ts = None
        self.raw_data_get_func = raw_data_get_func
        self.get()  # initialize self.prev
    def compute(self, current, current_ts):
        # currents is current data, current ts is a timestamp
        return {}
    def get(self):
        # 需要用户自己定义
        current = self.raw_data_get_func()
        current_ts = time.time()
        if self.prev:
            data = self.compute(current, current_ts)
        else:
            data = {}
        self.prev = current
        self.prev_ts = current_ts
        return data




class DiskIopsUsage(Usage):
    def __init__(self):
        Usage.__init__(self, psutil.disk_io_counters)

    def compute(self, current, current_ts):
        time_diff = current_ts - self.prev_ts
        busy_diff = float((current.busy_time - self.prev.busy_time)) / 1000  # ms to seconds
        read_time_diff = float(current.read_time- self.prev.read_time) / 1000
        write_time_diff = float(current.write_time- self.prev.write_time) / 1000
        utilization = (busy_diff / time_diff) * 100.0
        read_utilization = (read_time_diff / time_diff) * 100.0
        write_utilization = (write_time_diff / time_diff) * 100.0
        read_bytes_diff = current.read_bytes - self.prev.read_bytes
        read_count_diff = current.read_count - self.prev.read_count
        write_bytes_diff = current.write_bytes - self.prev.write_bytes
        write_count_diff = current.write_count - self.prev.write_count
        read_bytes_per_s = read_bytes_diff / time_diff
        read_count_per_s = read_count_diff / time_diff
        write_bytes_per_s = write_bytes_diff / time_diff
        write_count_per_s = write_count_diff / time_diff
        data = dict(
            util = utilization,
            read_util = read_utilization,
            write_util = write_utilization,
            read_speed = read_bytes_per_s,
            read_speed_for_human = bytes2human(read_bytes_per_s),
            write_speed = write_bytes_per_s,
            write_speed_for_human = bytes2human(write_bytes_per_s),
            read_count_speed = read_count_per_s,
            write_count_speed = write_count_per_s
        )
        return data





def get_net_io_raw_data():
    data = psutil.net_io_counters(pernic=True)
    return data

class NetUsage(Usage):
    def __init__(self):
        Usage.__init__(self, get_net_io_raw_data)
    def compute(self, current, current_ts):
        time_diff = current_ts - self.prev_ts
        net_interfaces = current.keys()
        data = {}
        for net_interface in net_interfaces:
            if net_interface in ['lo']:
                continue
            if net_interface.startswith('veth') and len(net_interface) >= 10: # interface from docker, not real
                continue
            if net_interface.startswith('docker'):
                continue
            if net_interface not in self.prev: # 必须也在 prev 中才能对比
                continue
            sent = current[net_interface].bytes_sent
            recv = current[net_interface].bytes_recv
            if not sent and not recv: # not working...
                continue
            bytes_sent_diff = sent - self.prev[net_interface].bytes_sent
            bytes_recv_diff = recv - self.prev[net_interface].bytes_recv
            send_speed = bytes_sent_diff / time_diff
            recv_speed = bytes_recv_diff / time_diff
            interface_data = dict(
                sent = sent,
                sent_for_human = bytes2human(sent),
                recv = recv,
                recv_for_human = bytes2human(recv),
                sent_speed = send_speed,
                recv_speed = recv_speed,
                sent_speed_for_human = bytes2human(send_speed),
                recv_speed_for_human = bytes2human(recv_speed)
            )
            data[net_interface] = interface_data
        return data





class ProcessesUsage(Usage):
    def __init__(self):
        Usage.__init__(self, get_processes_raw_data)
    def compute(self, current, current_ts):
        time_diff = current_ts - self.prev_ts
        processes_info = current
        for pid, process_info in processes_info.items():
            pre_process_info = self.prev.get(pid)
            if not pre_process_info:
                continue
            process_io_info = process_info['io']
            pre_process_io_info = pre_process_info['io']
            read_bytes_diff = get_diff_value(process_io_info, pre_process_io_info, 'read_bytes')
            if pid == 2032:
                print read_bytes_diff
                print process_io_info
                print pre_process_io_info
            read_count_diff = get_diff_value(process_io_info, pre_process_io_info, 'read_count')
            write_bytes_diff = get_diff_value(process_io_info, pre_process_io_info, 'write_bytes')
            write_count_diff = get_diff_value(process_io_info, pre_process_io_info, 'write_count')
            read_bytes_per_s = read_bytes_diff / time_diff
            read_count_per_s = read_count_diff / time_diff
            write_bytes_per_s = write_bytes_diff / time_diff
            write_count_per_s = write_count_diff / time_diff
            io_speed_info =  dict(
                read_speed = read_bytes_per_s,
                read_speed_for_human = bytes2human(read_bytes_per_s),
                write_speed = write_bytes_per_s,
                write_speed_for_human = bytes2human(write_bytes_per_s),
                read_count_speed = read_count_per_s,
                write_count_speed = write_count_per_s
            )
            process_io_info.update(io_speed_info)
        return processes_info







############# utils for usage #############

io_usage_obj = None
net_usage_obj = None
processes_usage_obj = None



def get_io_usage():
    global io_usage_obj
    if not io_usage_obj:
        io_usage_obj = DiskIopsUsage()
    return io_usage_obj.get()


def get_net_usage():
    global net_usage_obj
    if not net_usage_obj:
        net_usage_obj = NetUsage()
    return net_usage_obj.get()


def get_processes_usage():
    global processes_usage_obj
    if not processes_usage_obj:
        processes_usage_obj = ProcessesUsage()
    return processes_usage_obj.get()







