"""这是“nester.py”模块，提供了一个名为print_lol()的函数，
用来打印列表，其中包含或不包含嵌套列表"""
def print_lol(the_list,indent=false,level=0):
    """这个函数有一个位置参数，名为“the_list”，
        这可以是任何python列表（包含或不包含嵌套列表），
        所提供列表中的各个数据项会（递归的）打印到屏幕上，而且各占一行。
        第二个参数（名为“indent”）开始时这个参数值设为False--也就是说，
        默认情况下不打开缩进特性。
        第三个个参数（名为“level”）用来在遇到嵌套列表时插入制表符，
        在不传入参数情况下默认为0--第一层的列表不进行缩进。
        """
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each_item)
