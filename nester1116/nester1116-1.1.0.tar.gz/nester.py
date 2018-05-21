'''
Created on 2018年5月18日
This is nester.py module, contains a function named print_lol which prints all items in a list
@author: mingshanjia
'''
def print_lol(the_list,level):
    #print all items in a multiple-layer list
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print('\t',end='')
            print(each_item)




    
