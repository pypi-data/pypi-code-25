def print_lol(x):
    for each_x in x:
        if(isinstance(each_x, list)):
            print_lol(each_x)
        else:
            print(each_x)