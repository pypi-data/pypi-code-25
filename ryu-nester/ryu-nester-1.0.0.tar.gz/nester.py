"""this is "nester.py" module providing one function called print_lol which print list that may or may not includie nested list"""
def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
