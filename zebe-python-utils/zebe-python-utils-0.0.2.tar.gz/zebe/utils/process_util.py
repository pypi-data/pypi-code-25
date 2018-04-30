# -*- coding: utf-8 -*-
import os


# 查找指定名称的python进程，返回进程ID列表
def find_python_process_by_name(name):
    pid_list = []
    cmd = "ps -ef| grep python"
    f = os.popen(cmd)
    txt = f.readlines()
    if len(txt) == 0:
        return False
    else:
        for line in txt:
            column_array = line.split()
            pid = column_array[1]
            for column in column_array:
                if str(column) == name:
                    pid_list.append(int(pid))
    return pid_list


# 杀死指定名称的python进程，返回杀死结果
def kill_python_process_by_name(name):
    pid_list = find_python_process_by_name(name)
    for i in range(len(pid_list)):
        cmd = "kill -9 %s" % str(pid_list[i])
        os.system(cmd)
    return len(find_python_process_by_name(name)) == 0
