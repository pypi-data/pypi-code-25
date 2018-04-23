"""这是“nester.py”模块，提供了一个名为print_lol的函数，
这个函数的作用是打印列表，其中有可能包含（也可能不包含）嵌套列表。"""

'''
movies=[
    "The Holy Grail",1975,"Terry Jones & Terry Gilliam",91,
        ["Graham Chapman",
            ["Michael Palin","John Cleese","Terry Gilliam","Eric Idle","Terry Jones"]]]
'''

def print_lol(the_list,level):
    """这个函数取一个未知参数，名为“the_list”，这可以是任何python列表
    （也可以是包含嵌套列表的列表）。所指定的列表中的每个数据项会（递归地）
    输出到屏幕上，各数据项各占一行。第二个参数（名为“level”）用来在遇到
    嵌套列表时插入制表符。"""
    for item in the_list:
        if isinstance(item,list):
            print_lol(item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(item)

