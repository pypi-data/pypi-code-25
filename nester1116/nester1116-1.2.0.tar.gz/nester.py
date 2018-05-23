'''
Created on 2018年5月18日
This is nester.py module, contains a function named print_lol which prints all items in a list
@author: mingshanjia
'''

import sys

def print_lol(the_list,indent=False,level=0,fh=sys.stdout):
    #print all items in a multiple-layer list
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item,indent,level+1,fh)
        else:
            if indent:
                for tab_stop in range(level):
                    print('\t',end='',file=fh)
            print(each_item,file=fh)




    
