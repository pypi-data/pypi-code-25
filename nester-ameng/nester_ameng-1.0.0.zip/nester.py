"""这是“nester.py”模块，提供了一个名为print_lol的函数，
这个函数的作用是打印列表，其中有可能包含（也可能不包含）嵌套列表。"""

def print_lol(the_list):
    """这个函数取一个未知参数，名为“the_list”，这可以是任何python列表
    （也可以是包含嵌套列表的列表）。所指定的列表中的每个数据项会（递归地）
    输出到屏幕上，各数据项各占一行。"""
    for item in the_list:
        if isinstance(item,list):
            print_lol(item)
        else:
            print(item)
