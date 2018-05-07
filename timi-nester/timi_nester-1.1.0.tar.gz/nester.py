
# -*- coding: utf-8 -*-
"""
Created on Wed May  2 00:38:37 2018

@author: OAyegbayo
"""

''''
    A recursive function to print the elements of a list
'''
def print_lol(_list, level):    
    for item in _list:
        if(isinstance(item, list)):
            print_lol(item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end="")                
            print(item)

print_lol(["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
["Graham Chapman", ["Michael Palin", "John Cleese",
"Terry Gilliam", "Eric Idle", "Terry Jones"]]], 0)