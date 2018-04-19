#!/usr/bin/env python

'''
	Contains all needed for creation any JSON members, selection JSON members from JSON, filtering of selection and and much more other
'''

# Define metadata
__version__ 	= '1.1.3'
__author__ 		= 'Vladimir Saltykov'
__copyright__ 	= 'Copyright 2017, Vladimir Saltykov'
__email__ 		= 'vowatchka@mail.ru'
__license__ 	= "MIT"
__date__ 		= '2017-12-14'

# Import modules and packages
import os
import re
import json
import copy

class JPathError(Exception):
	'''
		Base JPath exception
	'''
	
	def __init__(self, message, lineno = None, pos = None):
		if lineno != None and pos != None:
			self._lineno 	= lineno
			self._pos 		= pos
			self._errmsg 	= '%s at line %d (position: %d)' % (message, self._lineno, self._pos)
		else:
			self._errmsg = '%s' % message
		Exception.__init__(self, self._errmsg)
		
	lineno 	= property()
	pos 	= property()
	errmsg 	= property()
	
	@lineno.getter
	def lineno(self):
		'''
			Line number where exception occurred in JPath. Readonly
		'''
		return self._lineno
		
	@pos.getter
	def pos(self):
		'''
			Char position where exception occurred in JPath. Readonly
		'''
		return self._pos
		
	@errmsg.getter
	def errmsg(self):
		'''
			Exception message. Readonly
		'''
		return self._errmsg
		
class JPLexicalError(JPathError):
	'''
		JPath lexical exception
	'''
	pass
	
class JPSyntaxError(JPathError):
	'''
		JPath syntax exception
	'''
	pass
	
class JPMethodError(JPathError):
	'''
		JPath method exception
	'''
	pass
		
class JMember(object):
	'''
		A member of JSON. Each of the member has some name and some value.
		The name always must be a string or None if the value equal root of JSON.
		The value can be one of the follow data types:
		* Object (dict() in Python)
		* Array (list() in Python)
		* Number:
		   * Integer (int() in Python)
		   * Float (float() in Python)
		* String (str() in Python)
		* Boolean (bool() in Python)
		* Null (None in Python)
	'''
	
	def __init__(self, name, value, transformed = []):
		'''
			Initializes a new member of JSON
		'''
		
		# Name of member must be a string
		if name != None and type(name) != type(str()):
			raise TypeError('Name of member must be a string')
		self._name = name
		
		# Expecting data types which are equivalent JSON data types
		if type(value) == type(dict()):
			valueType = 'JObject'
		elif type(value) == type(list()):
			valueType = 'JArray'
		elif type(value) == type(int()):
			valueType = 'JInt'
		elif type(value) == type(float()):
			valueType = 'JFloat'
		elif type(value) == type(str()):
			valueType = 'JString'
		elif type(value) == type(bool()):
			valueType = 'JBool'
		elif type(value) == type(None):
			valueType = 'JNull'
		else:
			raise TypeError('Unexpected type "' + stype(value) + '"')
			
		# Checking that given value is correct
		# if self._name == None and transformed == [] and type(value) != type(dict()) and type(value) != type(list()):
			# raise ValueError('JSON must be a object or an array')
			
		self._value = value
		self._valueType = valueType
		
		if type(transformed) == type(list()):
			self._transformed = transformed
		else:
			raise TypeError('argument \'transformed\' must be a list')
		
	def s(self, pretty = False):
		'''
			Serializes self. It can be pretty serialized if you specified True as value of @pretty
		'''
		if self._name != None:
			for_pretty = {self._name : self._value}
		else:
			for_pretty = self._value
		return json.dumps(for_pretty, indent = ' ' * 4 if type(pretty) == type(bool()) and pretty else None)
		
	def __str__(self):
		'''
			Returns str({self.name : self.value})
		'''
		return str({self._name : self._value})
		
	name 		= property()
	value 		= property()
	valueType 	= property()
	transformed = property()
	
	@name.getter
	def name(self):
		'''
			A some name of JSON member. Read/Write
		'''
		return self._name
		
	@name.setter
	def name(self, value):
		'''
			A some name of JSON member. Read/Write
		'''
		# Name of member must be a string
		if value != None and type(value) != type(str()):
			raise TypeError('Name of member must be a string')
		self._name = value
			
	@value.getter
	def value(self):
		'''
			A some value of JSON member. Readonly
		'''
		return self._value
		
	@valueType.getter
	def valueType(self):
		'''
			A type of JSON member value. Readonly
		'''
		return self._valueType
		
	@transformed.getter
	def transformed(self):
		'''
			List of JPath functions which were applied to JSON member value. Functions follow in order of they be applied. Readonly
		'''
		return copy.deepcopy(self._transformed)
		
class JMembers(object):
	'''
		Sequence of JSON members which were selected by JPath query
	'''

	def __init__(self):
		'''
			Initializes the empty sequence of JSON members
		'''
		self._list = []
	
	def __getitem__(self, idx):
		'''
			Returns one of the JSON members by his index
		'''
		if isinstance(idx, slice):
			return JMembers.create(self._list[idx.start : idx.stop : idx.step])
		else:
			try:
				return copy.deepcopy(self._list[idx])
			except IndexError:
				raise IndexError('Index out of range')
			except TypeError:
				raise TypeError('Indices must be integers or slices, not str')
			
	def __len__(self):
		'''
			Returns count of the JSON members in sequence
		'''
		return len(self._list)
	
	def __iter__(self):
		'''
			Returns self
		'''
		self.__index = -1
		return self
		
	def __next__(self):
		'''
			Returns a next member from JSON members sequence
		'''
		self.__index += 1
		if self.__index >= len(self._list):
			raise StopIteration
		return self._list[self.__index]
		
	def __str__(self):
		'''
			Retunrs str(self.list)
		'''
		l = []
		for el in self._list:
			l.append({el.name : el.value})
		return str(l)
	
	def __add(self, *args):
		'''
			Adds a new member to the end of JSON members sequence
		'''
		if len(args) > 0:
			members = args[0] if type(args[0]) == type(list()) else [args[0]]
			for m in members:
				if not isinstance(m, JMember):
					raise TypeError('Can\'t add element to sequence of members. Expected JMember (not ' + stype(m) + ')')
				self._list.append(m)
				
	@staticmethod
	def create(*args):
		'''
			Creates a new sequence of JSON members.
			If argument isn\'t specified, creates the empty sequence.
			If argument is specified as an instance of JMember, creates a new sequence of JSON members with the one element.
			If argument is specified as list of an instances of JMember, creates a new sequence of JSON members that contains all elements from list
		'''
		
		if len(args) > 1:
			raise TypeError('create expected at most 1 argument but got ' + str(len(args)))
		jms = JMembers()
		jms.__add(*args)
		return jms
		
	def item(self, idx):
		'''
			Returns one of the JSON members by his index
		'''
		return self.__getitem__(idx)
		
	def s(self, pretty = False):
		'''
			Serializes self. It can be pretty serialized if you specified True as value of @pretty
		'''
		for_pretty = []
		for el in self._list:
			for_pretty.append({el.name : el.value} if el.name != None else el.value)
		return json.dumps(for_pretty, indent = ' ' * 4 if type(pretty) == type(bool()) and pretty else None)
		
	list 	= property()
	count 	= property()
	
	@list.getter
	def list(self):
		'''
			Sequence of JSON members. Readonly
		'''
		return copy.deepcopy(self._list)
		
	@count.getter
	def count(self):
		'''
			Count of JSON members in sequence. Readonly
		'''
		return len(self._list)

class Stack(object):
	'''
		Some stack
	'''
	
	def __init__(self):
		'''
			Initialize empty stack
		'''
		self._stack = []
			
	def __len__(self):
		'''
			Returns length of stack
		'''
		return len(self._stack)
		
	def __str__(self):
		return str(self._stack)
		
	def push(self, value):
		'''
			Push a new element to top of stack
		'''
		self._stack.append(value)
		
	def pop(self):
		'''
			Delete element from top of stack and return it
		'''
		if not self.isempty():
			return self._stack.pop()
		else:
			raise IndexError('Stack is empty')
			
	def isempty(self):
		'''
			Return true if stack is empty, otherwise false
		'''
		return True if not len(self._stack) else False
		
	top 	= property()
	bottom 	= property()
	
	@top.getter
	def top(self):
		'''
			Return top of stack. Readonly
		'''
		if not self.isempty():
			return copy.deepcopy(self._stack[len(self._stack) - 1])
		else:
			raise IndexError('Stack is empty')
		
	@bottom.getter
	def bottom(self):
		'''
			Return bottom of stack. Readonly
		'''
		if not self.isempty():
			return copy.deepcopy(self._stack[0])
		else:
			raise IndexError('Stack is empty')
		
def stype(obj, postfix = ''):
	'''
		Returns short type name of object. You can add needed information to the end of type name if you will be specify postfix
	'''
	t = re.sub(r'<\s*class\s+\'([\.\w+]+?)\'\s*>', r'\1' + postfix, str(type(obj)))
	return t.split('.').pop()
		
def get_str_from_parsing(p):
	'''
		Concatenates string from parts that were be given by parsing
	'''
	s = ''
	for i in range(len(p.slice)):
		if i == 0:
			continue
		s += str(p[i])
	return s

def select(selector, name, members):
	'''
		Returns the new instance of JMembers that will be created from selected JSON members.
		* @selector can be the simple selection operator (.) or the deep selection operator (..)
		* @name is some name of selectable JSON member
		* @members is the instance of JMembers from that will be selected all JSON members if they will be finded by their name specified as @name
	'''
	out_members = []
	for member in members:
		out_members += select_all_members(name, member.value).list if selector == '..' else select_one_member(name, member.value).list
	return JMembers.create(out_members)

def select_all_members(name, from_obj):
	'''
		Returns the new instance of JMembers that will be created from selected JSON members. It function uses deep selection.
		* @name is some name of selectable JSON member
		* @from_obj is JSON (for example, it's dictionary or list for Python) from that will be selected all JSON members if they will be finded by their name specified as @name
	'''
	members = []
	if type(from_obj) != type(list()):
		members = select_one_member(name, from_obj).list
	values = []
	if type(from_obj) == type(dict()):
		keys = list(from_obj.keys())
		keys.sort()
		values = [from_obj[key] for key in keys]
	elif type(from_obj) == type(list()):
		values = from_obj

	if len(values):  
		for val in values:
			members += select_all_members(name, val)
	return JMembers.create(members)

def select_one_member(name, from_obj):
	'''
		Returns the new instance of JMembers that will be created from selected JSON members. It function uses simple selection.
		* @name is some name of selectable JSON member
		* @from_obj is Python object (usually dict or list) from that will be selected all JSON members if they will be finded by their name specified as @name
	'''
	members = []
	if type(from_obj) == type(dict()):
		if name == '*':
			keys = list(from_obj.keys())
			keys.sort()
			for key in keys:
				members += select_one_member(key, from_obj).list
		else:
			try:
				value = from_obj[name]
				return JMembers.create(JMember(name, value))
			except:
				pass
				#if type(value) != type(list()):
				#else:
					#return [JMember(prop_name, val) for val in value]
	elif type(from_obj) == type(list()):
		for el in from_obj:
			members += select_one_member(name, el).list
	
	return JMembers.create(members)

def disclosure_list(members):
	'''
		Returns the new instance of JMembers that will be created from sequence of JSON members specified as @members.
		However if value of JSON member is list, it will be disclosured that means that all elements from list will be added to output as the instances of JMember
		* @members is the instance of JMembers
	'''
	out_members = []
	for member in members:
		out_members += [JMember(member.name, el) for el in member.value] if type(member.value) == type(list()) else [member]
	return JMembers.create(out_members)
	
def filtering(filter, members):
	'''
		Returns the new instance of JMembers that will be created from sequence of JSON members specified as @members, but first it will be filtered.
		Filter can be a index or list of indexes. If index is out of range, value by it will be not added to output. Also filter can be a dictionary with keys 'start', 'stop' and 'step'. Values of this keys will be used as slice.
		* @filter is filter that will be applied
		* @members is the instance of JMembers
	'''
	if type(filter) == type(int()):
		idx = filter
		try:
			filtered_member = members[idx]
			return JMembers.create(filtered_member)
		except:
			# Index out of range
			return JMembers.create()
	elif type(filter) == type(list()):
		out_members = []
		for idx in filter:
			if idx >= 0 and idx < members.count:
				out_members.append(members[idx])
		return JMembers.create(out_members)
	elif type(filter) == type(dict()):
		return JMembers.create(members[filter['start'] : filter['stop'] : filter['step']].list)
		
def apply_func(func_name, params, members):
	'''
		Returns the new instance of JMembers that will be created from results that will be returned by specified JPath function for each of JSON member. Function apply to value of each JSON member.
		* @func_name is function that will be applied. See full list of functions in the docs of JPath
		* @params is the list of function parameters (it must be empty list if function don\'t takes parameters)
		* @members is the instance of JMembers
	'''
	def call(func_name, params, value):
		def toint(value, *args):
			if len(args):
				raise JPathError('toint() takes 0 arguments but ' + str(len(args)) + ' were given')
			return int(float(value))
		def toflt(value, *args):
			if len(args):
				raise JPathError('toflt() takes 0 arguments but ' + str(len(args)) + ' were given')
			return float(value)
		def tostr(value, *args):
			if len(args):
				raise JPathError('tostr() takes 0 arguments but ' + str(len(args)) + ' were given')
			return str(value)
		def val(value, *args):
			if len(args):
				raise JPathError('val() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value
		def length(value, *args):
			if len(args):
				raise JPathError('length() takes 0 arguments but ' + str(len(args)) + ' were given')
			if type(value) == type(list()) or type(value) == type(dict()):
				return len(value) 
			else:
				raise TypeError('Expected list or dictionary')
		def isnum(value, *args):
			if len(args):
				raise JPathError('isnum() takes 0 arguments but ' + str(len(args)) + ' were given')
			return True if (type(value) == type(int()) or type(value) == type(float())) else False
		def isint(value, *args):
			if len(args):
				raise JPathError('isint() takes 0 arguments but ' + str(len(args)) + ' were given')
			return True if type(value) == type(int()) else False
		def isflt(value, *args):
			if len(args):
				raise JPathError('isflt() takes 0 arguments but ' + str(len(args)) + ' were given')
			return True if type(value) == type(float()) else False
		def isbool(value, *args):
			if len(args):
				raise JPathError('isbool() takes 0 arguments but ' + str(len(args)) + ' were given')
			return True if type(value) == type(bool()) else False
		def isstr(value, *args):
			if len(args):
				raise JPathError('isstr() takes 0 arguments but ' + str(len(args)) + ' were given')
			return True if type(value) == type(str()) else False
		def isnull(value, *args):
			if len(args):
				raise JPathError('isnull() takes 0 arguments but ' + str(len(args)) + ' were given')
			return True if type(value) == type(None) else False
		def isarr(value, *args):
			if len(args):
				raise JPathError('isarr() takes 0 arguments but ' + str(len(args)) + ' were given')
			return True if type(value) == type(list()) else False
		def isobj(value, *args):
			if len(args):
				raise JPathError('isobj() takes 0 arguments but ' + str(len(args)) + ' were given')
			return True if type(value) == type(dict()) else False
		def rnd(value, *args):
			if len(args) == 0 or len(args) > 1:
				raise JPathError('rnd() takes 1 argument but ' + str(len(args)) + ' were given')
			if type(args[0]) != type(int()):
				raise JPathError('Invalid type of argument \'digits\' for rnd(): Integer expected')
			return round(value, args[0])
		def strlen(value, *args):
			if len(args):
				raise JPathError('strlen() takes 0 arguments but ' + str(len(args)) + ' were given')
			if type(value) == type(str()):
				return len(value)
			else:
				raise TypeError('Expected string')
		def substr(value, *args):
			if len(args) < 2 or len(args) > 2:
				raise JPathError('substr() takes 2 arguments but ' + str(len(args)) + ' were given')
			if type(args[0]) != type(int()):
				raise JPathError('Invalid type of argument \'startIdx\' for substr(): Integer expected')
			if type(args[1]) != type(int()):
				raise JPathError('Invalid type of argument \'length\' for substr(): Integer expected')
			if type(value) == type(str()):
				return value[args[0]:args[1]+1]
			else:
				raise TypeError('Expected string')
		def replace(value, *args):
			if len(args) < 2 or len(args) > 2:
				raise JPathError('replace() takes 2 arguments but ' + str(len(args)) + ' were given')
			if type(args[0]) != type(str()):
				raise JPathError('Invalid type of argument \'template\' for replace(): String expected')
			if type(args[1]) != type(str()):
				raise JPathError('Invalid type of argument \'replacement\' for replace(): String expected')
			return value.replace(args[0], args[1])
		def isdigit(value, *args):
			if len(args):
				raise JPathError('isdigit() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.isdigit()
		def isalpha(value, *args):
			if len(args):
				raise JPathError('isalpha() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.isalpha()
		def isalnum(value, *args):
			if len(args):
				raise JPathError('isalnum() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.isalnum()
		def islower(value, *args):
			if len(args):
				raise JPathError('islower() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.islower()
		def isupper(value, *args):
			if len(args):
				raise JPathError('isupper() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.isupper()
		def isspace(value, *args):
			if len(args):
				raise JPathError('isspace() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.isspace()
		def istitle(value, *args):
			if len(args):
				raise JPathError('istitle() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.istitle()
		def lower(value, *args):
			if len(args):
				raise JPathError('lower() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.lower()
		def upper(value, *args):
			if len(args):
				raise JPathError('upper() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.upper()
		def startswith(value, *args):
			if len(args) == 0 or len(args) > 1:
				raise JPathError('startswith() takes 1 argument but ' + str(len(args)) + ' were given')
			if type(args[0]) != type(str()):
				raise JPathError('Invalid type of argument \'template\' for startswith(): String expected')
			return value.startswith(args[0])
		def endswith(value, *args):
			if len(args) == 0 or len(args) > 1:
				raise JPathError('endswith() takes 1 argument but ' + str(len(args)) + ' were given')
			if type(args[0]) != type(str()):
				raise JPathError('Invalid type of argument \'template\' for endswith(): String expected')
			return value.endswith(args[0])
		def capitalize(value, *args):
			if len(args):
				raise JPathError('capitalize() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.capitalize()
		def ltrim(value, *args):
			if len(args):
				raise JPathError('ltrim() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.lstrip()
		def rtrim(value, *args):
			if len(args):
				raise JPathError('rtrim() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.rstrip()
		def trim(value, *args):
			if len(args):
				raise JPathError('trim() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.strip()
		def title(value, *args):
			if len(args):
				raise JPathError('title() takes 0 arguments but ' + str(len(args)) + ' were given')
			return value.title()
		def contains(value, *args):
			if len(args) == 0 or len(args) > 1:
				raise JPathError('contains() takes 1 argument but ' + str(len(args)) + ' were given')
			if type(args[0]) != type(str()):
				raise JPathError('Invalid type of argument \'template\' for contains(): String expected')
			return True if value.find(args[0]) != -1 else False
		def normalize(value, *args):
			if len(args):
				raise JPathMethodError('normalize() takes 0 arguments but ' + str(len(args)) + ' were given')
			return re.sub(r'\s+', ' ', re.sub(r'[\r\n\t\v\f]+', '', value, re.I)).strip()
		def count(value, *args):
			if len(args):
				raise JPathError('count() takes 0 arguments but ' + str(len(args)) + ' were given')
			return len(value)
		def all(value, *args):
			if len(args):
				raise JPathError('all() takes 0 arguments but ' + str(len(args)) + ' were given')
			for m in value:
				if not m.value:
					return False
			return True
		def any(value, *args):
			if len(args):
				raise JPathError('any() takes 0 arguments but ' + str(len(args)) + ' were given')
			for m in value:
				if m.value:
					return True
			return False
			
		try:
			return eval(func_name + '(value, *params)')
		except JPathError as ex1:
			raise ex1
		except Exception as ex2:
			return ex2

	func_list = [
					'toint', 'toflt', 'tostr', 'val', 'length', 
					'isnum', 'isint', 'isflt', 'isbool', 'isstr', 'isnull', 'isobj', 'isarr',
					'rnd',
					'strlen', 'substr', 'replace', 'isdigit', 'isalpha', 'isalnum', 'islower', 'isupper',
					'isspace', 'istitle', 'lower', 'upper', 'startswith', 'endswith', 'capitalize',
					'ltrim', 'rtrim', 'trim', 'title', 'contains', 'normalize',
					'count', 'all', 'any'
				]
	out_members = []
	if func_name in func_list:
		for member in members:
			if func_name in ['count', 'all', 'any']:
				val = call(func_name, params, members.list)
			else:
				val = call(func_name, params, member.value)
			out_members += [JMember(member.name, val, transformed = member.transformed + [func_name])] if not isinstance(val, Exception) else []
			if func_name in ['count', 'all', 'any']:
				break
		return JMembers.create(out_members)
	else:
		raise JPathError('Unknown function ' + func_name + '()')