#!/usr/bin/env python

'''
	Contains functions and rules of parsing and executing JPath query
'''

# Define metadata
__version__ 	= '1.1.1'
__author__ 		= 'Vladimir Saltykov'
__copyright__ 	= 'Copyright 2017, Vladimir Saltykov'
__email__ 		= 'vowatchka@mail.ru'
__license__ 	= "MIT"
__date__ 		= '2017-12-13'

__all__ = ['jquery', 'parser']

# Import modules and packages
import os
import copy
import ply.lex as lex
import ply.yacc as yacc
import jpathpy.utils as utils

# Import rules of parsing
from jpathpy.jlexer import *
from jpathpy.jparsers.jexpr import *
from jpathpy.jparsers import jfexpr

parser 		= None
jobj_stack 	= utils.Stack()

def jquery(jpath, jobj):
	'''
		Executes JPath query and returns result of executing
		* @jpath is JPath query specified as an string
		* @jobj is object from that will be selected JSON members
	'''

	# Define grammar rules
	def p_result(p):
		'''result : jpathquery
				  | union'''
		# Rule for parsing a result of JPath query. It will be first rule
		p[0] = p[1]
	
	def p_jpathquery(p):
		'''jpathquery : jpath
					  | transformed'''
		# Rule for parsing JPath expression
		p[0] = p[1]
		
	def p_union(p):
		'''union : jpathquery UNION jpathquery
				 | union UNION jpathquery'''
		# Rule for parsing union of JPath expressions
		p[0] = utils.JMembers.create(p[1].list + p[3].list)
		
	def p_jpath_root(p):
		'''jpath : ROOT'''
		# Rule for parsing part of JPath expression as reference to the root of JSON
		try:
			p[0] = utils.JMembers.create(utils.JMember(None, jobj_stack.top))
		except:
			p[0] = utils.JMembers.create()
			
	def p_jpath_selection(p):
		'''jpath : jpath SIMPLESELECTOR STRING
				 | jpath SIMPLESELECTOR MULT
				 | jpath DEEPSELECTOR STRING
				 | jpath DEEPSELECTOR MULT'''
		# Rule for parsing part of JPath expression as simple of deep selection
		p[0] = utils.select(p[2], p[3] if p[3] == '*' else p[3][1:len(p[3])-1], p[1])
	
	def p_jpath_filterlist(p):
		'''jpath : jpath SIMPLESELECTOR LSQUAREPAREN int RSQUAREPAREN
				 | jpath SIMPLESELECTOR LSQUAREPAREN indexesstr RSQUAREPAREN
				 | jpath SIMPLESELECTOR LSQUAREPAREN slicestr RSQUAREPAREN'''
		# Rule for parsing part of JPath expression as filtering list
		members = p[1]
		out_members = []
		for member in members:
			if type(member.value) == type(list()):
				# create JMembers from elements in list
				members_from_list = utils.JMembers.create([utils.JMember(member.name, el) for el in member.value])
				
				# select specified members
				filtered_members_from_list = []
				if (str(p.slice[4]) == 'int'):
					idx = p[4]
					filtered_members_from_list = utils.filtering(idx, members_from_list)
				elif (str(p.slice[4]) == 'indexesstr'):
					indexes = [int(idx.strip()) for idx in p[4].split(',')]
					filtered_members_from_list = utils.filtering(indexes, members_from_list)
				elif str(p.slice[4]) == 'slicestr':
					sliceparams = [( int(param.strip()) if param != '' else None) for param in p[4].split(':')]
					slice = {
								'start': 	sliceparams[0],
								'stop': 	sliceparams[1],
								'step': 	( sliceparams[2] if len(sliceparams) > 2 else None )
							}
					filtered_members_from_list = utils.filtering(slice, members_from_list)
				
				# create new JMember for output
				# JMember value creates from early selected members
				out_members += [ utils.JMember(member.name, [m.value for m in filtered_members_from_list]) ]
		p[0] = utils.JMembers.create(out_members)
	
	def p_jpath_filtered(p):
		'''jpath : jpath LSQUAREPAREN indexesstr RSQUAREPAREN
				 | jpath LSQUAREPAREN slicestr RSQUAREPAREN
				 | jpath LSQUAREPAREN expressionstr RSQUAREPAREN
				 | jpath LSQUAREPAREN MULT RSQUAREPAREN'''
		# Rule for parsing part of JPath expression as filtering expression
		members = p[1]
		if (p[3] == '*'):
			# disclosure list
			p[0] = utils.disclosure_list(members)
		elif str(p.slice[3]) == 'expressionstr':
			try:
				# take member by index
				idx = int(p[3])
				p[0] = utils.filtering(idx, members)
			except:
				out_members = []
				# calculating filter expression
				for member in members:
					condition = jfexpr.jfexpression(p[3], member.value, jobj_stack.bottom)
					if condition:
						out_members.append(member)
				p[0] = utils.JMembers.create(out_members)
		elif str(p.slice[3]) == 'indexesstr':
			# take members by indexes
			indexes = [int(idx.strip()) for idx in p[3].split(',')]
			p[0] = utils.filtering(indexes, members)
		elif str(p.slice[3]) == 'slicestr':
			# take members by slice
			sliceparams = [( int(param.strip()) if param != '' else None) for param in p[3].split(':')]
			slice = {
						'start': 	sliceparams[0],
						'stop': 	sliceparams[1],
						'step': 	( sliceparams[2] if len(sliceparams) > 2 else None )
					}
			p[0] = utils.filtering(slice, members)
	
	def p_parameters_one(p):
		'''parameters : STRING
					  | int
					  | float'''
		# Rule for parsing available data types of function arguments
		
		# returning list of parameters
		if type(p[1]) == type(int()) or type(p[1]) == type(float()):
			p[0] = [ p[1] ]
		else:
			p[0] = [ p[1][1:len(p[1])-1] ]
			
	def p_parameters_group(p):
		'''parameters : parameters DELIMPARAMS parameters'''
		# Rule for parsing a list of arguments
		p[0] = p[1] + p[3]
	
	def p_function(p):
		'''function : SIMPLESELECTOR FUNCNAME LPAREN RPAREN
					| SIMPLESELECTOR FUNCNAME LPAREN parameters RPAREN'''
		# Rule for parsing JPath function
		if len(p) == 5:
			function = p[2]
			parameters = []
		else:
			function = p[2]
			parameters = p[4]
		p[0] = {
					'function': 	function,
					'parameters': 	parameters
			   }
	
	def p_transformed(p):
		'''transformed : jpath function
					   | transformed function'''
		# Rule for parsing part of JPath expression as JPath function
		try:
			p[0] = utils.apply_func(p[2]['function'], p[2]['parameters'], p[1])
		except Exception as ex:
			raise utils.JPMethodError(str(ex))
	
	# Define error rule
	def p_error(t):
		if t == None:
			raise utils.JPSyntaxError('Unexpected end of JPath query')
		else:
			# while True:
				# tok = parser.token()
				# if not tok:
					# break
				# print(tok)
			raise utils.JPSyntaxError('Unexpected token "' + str(t.value) + '"', t.lineno, t.lexpos)
	
	
	#Push to stack
	jobj_stack.push(copy.deepcopy(jobj))
	
	path = os.path.join(os.path.dirname(__file__), 'output')
	if not os.path.exists(path):
		os.mkdir(path)
	
	# Init lexer
	lexer = lex.lex(optimize = True, lextab = 'jlexertab', outputdir = path)
	
	# Init parser
	global parser
	if parser == None:
		parser = yacc.yacc(start = 'result', optimize = True, tabmodule = 'jquerytab', debugfile = 'jquery.out', outputdir = path)
	
	# Parse and exeute JPath
	result = parser.parse(jpath)
	
	# Pop from stack
	jobj_stack.pop()
	
	# Return
	return result