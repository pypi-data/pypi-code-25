def fd(*obj):
	"""Help on function fd:

fd(...)
	fd([object]) -> NoneType
	
	If called without an argument, display this help.
	Else, display an alphabetized list of names comprising (some of) the attributes of the given object, and of attributes reachable from it.
	This function shows the same result what dir function, with the difference that output is formatted in equal columns not in rows.
	
	"""
	if len(obj)==0:
		print(fd.__doc__)
		return None
	elif len(obj)==1:
		items = dir(obj[0])
	else:
		raise TypeError('fd expected at most 1 arguments, got '+str(len(obj)))
	
	offset = 1
	from math import ceil
	from sys import version_info
	if version_info.major < 3:
		offset = 0 

	dunder_methods = []
	all_rest_methods = []

	for item in items:
		if item.startswith('__'):
			dunder_methods.append(item)
		else:
			all_rest_methods.append(item)
	del items
	
	if len(dunder_methods)!=0:
	
		max_width_first_column = str(max([len(x)+1 for x in dunder_methods[0:int(len(dunder_methods)/3)+offset]]))
		max_width_second_column = str(max([len(x)+1 for x in dunder_methods[int(len(dunder_methods)/3)+offset:(int(len(dunder_methods)/3)*2)+offset]]))
		max_width_third_column = str(max([len(x) for x in dunder_methods[int(len(dunder_methods)/3)*2:]]))
	
		divider = int(ceil(len(dunder_methods)/3))
		for pos in range(divider):
			first = dunder_methods[0+pos]
			second = str(dunder_methods[divider+pos:divider+pos+1]).replace('[', '').replace(']', '')
			third = str(dunder_methods[divider*2+pos:divider*2+pos+1]).replace('[', '').replace(']', '')
			query = "%-" +max_width_first_column+"s" + "%-" +max_width_second_column+"s" + "%-" +max_width_third_column+"s"
			print(query%(first, second[1:-1], third[1:-1]))
	
	if len(all_rest_methods)!=0:
		print('')
		
		max_width_first_column = str(max([len(x)+1 for x in all_rest_methods[0:int(len(all_rest_methods)/3)+offset]]))
		max_width_second_column = str(max([len(x)+1 for x in all_rest_methods[int(len(all_rest_methods)/3)+offset:(int(len(all_rest_methods)/3)*2)+offset]]))
		max_width_third_column = str(max([len(x) for x in all_rest_methods[int(len(all_rest_methods)/3)*2:]]))
	
		divider = int(ceil(len(all_rest_methods)/3))
		for pos in range(divider):
			first = all_rest_methods[0+pos]
			second = str(all_rest_methods[divider+pos:divider+pos+1]).replace('[', '').replace(']', '')
			third = str(all_rest_methods[divider*2+pos:divider*2+pos+1]).replace('[', '').replace(']', '')
			query = "%-" +max_width_first_column+"s" + "%-" +max_width_second_column+"s" + "%-" +max_width_third_column+"s"
			print(query%(first, second[1:-1], third[1:-1]))
			
	return None
