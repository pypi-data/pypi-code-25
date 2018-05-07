"""
这是"nester.py"模块，提供了一个名为print_lol()的函数，这个函数的作用是打印列表，
其中有可能包含（也有可能不包含）嵌套列表
"""

def print_lol(the_list,level = 0):
    """
    这个函数取一个位置参数，名为“Tthe_list”.这可以是任何Python
    列表（或者含有列表的列表）。所指定的列表中的每个数据项会（递归地）
    输出在屏幕上，各数据占一行
    """
    for item in the_list:
        if isinstance(item,list):
            print_lol(item,level+1);
        else:
            print(item);
