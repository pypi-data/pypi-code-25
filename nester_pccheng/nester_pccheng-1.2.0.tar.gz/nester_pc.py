"""This is the "nester.py" module"""

def print_lol(the_list ,level=0):
        """takes an list, print each item in the list recurrsively.
                and on its own line"""
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,level+1)
                else:
                        for tap_range in range(level):
                                print("\t", end='')
                        print(each_item)
		
