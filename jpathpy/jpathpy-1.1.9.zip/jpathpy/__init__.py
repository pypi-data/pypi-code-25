#!/usr/bin/env python

'''
	Contains instruments for selection JSON members from JSON by using JPath syntax
'''

# Define metadata
__version__ 	= '1.1.7'
__author__ 		= 'Vladimir Saltykov'
__copyright__ 	= 'Copyright 2017, Vladimir Saltykov'
__email__ 		= 'vowatchka@mail.ru'
__license__ 	= "MIT"
__date__ 		= '2017-12-15'

__all__ = ['select_members']

# Import modules and packages
import json
import random
import jpathpy.utils as utils
import jpathpy.jparsers.jquery as jquery

# Define constants
ALL = 'ALL'
ANY = 'ANY'

def select_members(jpath, jdoc, mode = ALL):
	'''
		Returns all of the selected JSON members which will be finded by JPath query
		* @jpath is JPath query specified as string
		* @jdoc is JSON from that will be selected JSON members. JSON must be dictionary or list and it must be serializable
		* @mode can takes follow values:
		   * jpath.ALL - it means that all selected JSON members will be returned
		   * jpath.ANY - it means that any selected JSON member will be returned. If sequence of JSON members is enpty, None will be returned
		   * integer - it means that one of the selected JSON members will be returned by his index. If index is out of range, None will be returned
		   * tuple - it means that slice of the selected JSON members will be returned
	'''
	if type(jdoc) != type(dict()) and type(jdoc) != type(list()):
		raise TypeError('JSON must be a object or an array')
		
	try:
		s = json.dumps(jdoc)
	except Exception as ex:
		raise ValueError('It\'s not JSON: ' + str(ex))
	
	if mode != ALL and \
	   mode != ANY and \
	   type(mode) != type(int()) and \
	   type(mode) != type(tuple()):
		raise TypeError('Invalid mode')
	
	result = jquery.jquery(jpath, jdoc)
	
	if mode == ALL:
		return result
	elif mode == ANY:
		try:
			return result[random.randint(0, len(result)-1)]
		except:
			return None
	elif type(mode) == type(int()):
		try:
			return result[mode]
		except:
			return None
	elif type(mode) == type(tuple()):
		start 	= mode[0] if len(mode) > 0 else None
		stop	= mode[1] if len(mode) > 1 else None
		step 	= mode[2] if len(mode) > 2 else None
		return result[start : stop : step]