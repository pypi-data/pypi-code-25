import sys
'''This is the "nester.py" module, and it provides one function called
	print_lol() which prints lists that may or may not include nested lists.'''
def print_lol(the_list, indent=False, level=0, outType=sys.stdout):
	'''This function takes a positional argument called "the_list", which is any
		Python list (of, possibly, nested lists) and "level", which is a int number represent data level. Each data item in the provided list is (recursively) 
		printed to the screen on its own line.'''
	for item in the_list:
		if isinstance(item, list):
			print_lol(item, indent, level+1, outType)
		else:
			if indent:
				for tab_step in range(level):
					print('\t', end='', file=outType)
			print(item, file=outType)
