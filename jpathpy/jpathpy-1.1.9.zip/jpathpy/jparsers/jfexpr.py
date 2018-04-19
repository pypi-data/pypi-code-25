#!/usr/bin/env python

'''
	Contains functions and rules of parsing and executing JPath filtering expression
'''

# Define metadata
__version__ 	= '1.1.1'
__author__ 		= 'Vladimir Saltykov'
__copyright__ 	= 'Copyright 2017, Vladimir Saltykov'
__email__ 		= 'vowatchka@mail.ru'
__license__ 	= "MIT"
__date__ 		= '2017-12-13'

__all__ = ['jfexpression', 'parser']

# Import modules and packages
import os
import copy
import ply.lex as lex
import ply.yacc as yacc
import jpathpy.utils as utils

# Import rules of parsing
from jpathpy.jlexer import *
from jpathpy.jparsers.jexpr import *
from jpathpy.jparsers import jquery

parser 			= None
jobj_stack 		= utils.Stack()
jmember_stack 	= utils.Stack()

def jfexpression(expr, jmember, jobj):
	'''
		Executes JPath filtering expression and returns result of executing
		* @expr is JPath filtering expression specified as an string
		* @jmember is current JSON member from that will be selected JSON members if will be finded JPath without reference to the root of JSON
		* @jobj is object from that will be selected JSON members if will be finded JPath with reference to the root of JSON
	'''

	# Define grammar rules
	def p_result(p):
		'''result : expression'''
		# Rule for parsing a result of a filtering expression. It will be first rule
		p[0] = p[1]

	def p_expression(p):
		'''expression : number
					  | FALSE
					  | TRUE
					  | NULL
					  | STRING
					  | jpathexprstr'''
		# Rule for parsing operands which can be used in a filtering expression
		if str(p.slice[1]) == 'jpathexprstr':
			# check negation token
			if (p[1][0:1]) == '!':
				is_neg = True
				jpathexpr = p[1][1:]
			else:
				is_neg = False
				jpathexpr = p[1]
			
			# executing jpath
			if jpathexpr[0:1] == '$':
				members = jquery.jquery(jpathexpr, jobj_stack.top)
				if members.count == 1 and members[0].transformed != []:
					p[0] = members[0].value
				else:
					p[0] = [m.value for m in members]
			else:
				members = jquery.jquery('$' + jpathexpr, jmember_stack.top)
				if not len(members):
					p[0] = False
				elif members.count == 1 and members[0].transformed != []:
					p[0] = members[0].value
				elif members.count > 1 and members[0].transformed != []:
					p[0] = utils.apply_func('any', [], members)[0].value
				else:
					p[0] = True
					
			# negate or not negate
			if is_neg:
				try:
					p[0] = not p[0]
				except:
					p[0] = False
		elif str(p.slice[1]) == 'number':
			p[0] = p[1]
		elif p[1] == 'false':
			p[0] = False
		elif p[1] == 'true':
			p[0] = True
		elif p[1] == 'null':
			p[0] = None
		else:
			p[0] = p[1][1:len(p[1])-1]

	def p_expression_uminus(p):
		'''expression : MINUS expression %prec UMINUS'''
		# Rule for parsing the operation unary minus
		try:
			p[0] = -p[2]
		except:
			p[0] = False
		
	def p_expression_math(p):
		'''expression : expression PLUS expression
					  | expression MINUS expression
					  | expression MULT expression
					  | expression DIV expression
					  | expression MOD expression'''
		# Rule for parsing an arithmetic operations
		try:
			if p[2] == '+':
				p[0] = p[1] + p[3]
			elif p[2] == '-':
				p[0] = p[1] - p[3]
			elif p[2] == '*':
				p[0] = p[1] * p[3]
			elif p[2] == '/':
				p[0] = p[1] / p[3]
			elif p[2] == '%':
				p[0] = p[1] % p[3]
		except:
			p[0] = False
		
	def p_expression_group(p):
		'''expression : LPAREN expression RPAREN'''
		# Rule for parsing a grouping of operations
		p[0] = p[2]
		
	def p_expression_comp(p):
		'''expression : expression EQ expression
					  | expression NE expression
					  | expression LT expression
					  | expression LE expression
					  | expression GT expression
					  | expression GE expression'''
		# Rule for parsing a comparation operations
		try:
			if p[2] == '=':
				p[0] = ( p[1] == p[3] )
			elif p[2] == '!=':
				p[0] = ( p[1] != p[3] )
			elif p[2] == '<':
				p[0] = ( p[1] < p[3] )
			elif p[2] == '<=':
				p[0] = ( p[1] <= p[3] )
			elif p[2] == '>':
				p[0] = ( p[1] > p[3] )
			elif p[2] == '>=':
				p[0] = ( p[1] >= p[3] )
		except:
			p[0] = False
		
	def p_expression_logic(p):
		'''expression : expression AND expression
					  | expression OR expression'''
		# Rule for parsing a logical operations
		try:
			if p[2] == 'and':
				p[0] = ( p[1] and p[3] )
			elif p[2] == 'or':
				p[0] = ( p[1] or p[3] )
		except:
			p[0] = False
	
	# Define error rule
	def p_error(t):
		if t == None:
			raise utils.JPSyntaxError('Unexpected end of expression')
		else:
			# while True:
				# tok = parser.token()
				# if not tok:
					# break
				# print(tok)
			raise utils.JPSyntaxError('Unexpected token "' + str(t.value) + '"', t.lineno, t.lexpos)
	
	
	# Push to stack
	jobj_stack.push(copy.deepcopy(jobj))
	jmember_stack.push(copy.deepcopy(jmember))
	
	path = os.path.join(os.path.dirname(__file__), 'output')
	if not os.path.exists(path):
		os.mkdir(path)
		
	# Init lexer
	lexer = lex.lex(optimize = True, lextab = 'jlexertab', outputdir = path)
	
	# Init parser
	global parser
	if parser == None:
		parser = yacc.yacc(start = 'result', optimize = True, tabmodule = 'jfexprtab', debugfile = 'jfexpr.out', outputdir = path)
	
	# Parse and execute filtering expression
	result = parser.parse(expr)
	
	# Pop from stack
	jobj_stack.pop()
	jmember_stack.pop()
	
	# Return
	return result