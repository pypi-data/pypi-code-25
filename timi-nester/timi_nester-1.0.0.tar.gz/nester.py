
# -*- coding: utf-8 -*-
"""
Created on Wed May  2 00:38:37 2018

@author: OAyegbayo
"""

''''
    A recursive function to print the elements of a list
'''
def print_lol(_list):    
    for item in _list:
        if(isinstance(item, list)):
            print_lol(item)
        else:
            print(item)