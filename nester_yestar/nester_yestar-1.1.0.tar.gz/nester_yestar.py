def print_lol(x,level):
    for each_x in x:
        if(isinstance(each_x, list)):
            print_lol(each_x,level+1)
        else:
			for tap_stop in range(levle):
				print("\t",end='')
            print(each_x)