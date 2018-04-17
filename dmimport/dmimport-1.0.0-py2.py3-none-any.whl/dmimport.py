#!/usr/bin/python
# coding:utf-8

import os, sys

class Import(object):

    @staticmethod
    def import_relative_paths(relative_paths):

		for relative_path in relative_paths:

            absolute_path = os.path.realpath(os.path.abspath(os.path.join(os.getcwd(), relative_path)))
	
     	    if(absolute_path not in sys.path):
	            sys.path.insert(0, absolute_path)


			
def main(argv):

	relative_paths = ["."]
	
	if(len(argv) > 1):
		relative_paths = argv[1:]

    Import.import_relative_paths(relative_paths)


	
if __name__ == "__main__":
    
	print("dmimport.Import.main", sys.argv)
    main(sys.argv)










	
	  
	  
	  
