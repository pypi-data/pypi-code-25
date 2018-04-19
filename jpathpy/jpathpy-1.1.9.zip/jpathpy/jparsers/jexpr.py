#!/usr/bin/env python

'''
	Contains rules of parsing JPath expression
'''

# Define metadata
__version__ 	= '1.0.0'
__author__ 		= 'Vladimir Saltykov'
__copyright__ 	= 'Copyright 2017, Vladimir Saltykov'
__email__ 		= 'vowatchka@mail.ru'
__license__ 	= "MIT"
__date__ 		= '2017-12-04'

# Import modules and packages
import jpathpy.utils as utils

# Define precedences
precedence = (
				('left', 'UNION'),
				('left', 'DELIMPARAMS', 'SLICE'),
				('left', 'LSQUAREPAREN', 'RSQUAREPAREN'),
				('left', 'AND', 'OR'),
				('left', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'),
				('left', 'PLUS', 'MINUS'),
				('left', 'MULT', 'DIV', 'MOD'),
				('right', 'UMINUS'),
			)
			
# Define grammar rules
def p_jpathexprstr(p):
	'''jpathexprstr : ROOT
					| NOT ROOT
					| ROOT fromcurrentstr
					| NOT ROOT fromcurrentstr
					| fromcurrentstr
					| NOT fromcurrentstr'''
	# Rule for parsing JPath expression. It wil be first rule
	p[0] = utils.get_str_from_parsing(p)
		
def p_fromcurrentstr(p):
	'''fromcurrentstr : selectionsequencestr
					  | transformsequencestr
					  | selectionsequencestr transformsequencestr'''
	# Rule for parsing selection expression from the current JSON members
	p[0] = utils.get_str_from_parsing(p)

def p_selectionsequencestr(p):
	'''selectionsequencestr : selectionstr
							| selectionsequencestr selectionstr'''
	# Rule for parsing a sequence of selections
	p[0] = utils.get_str_from_parsing(p)
		
def p_transformsequencestr(p):
	'''transformsequencestr : transformstr
							| transformsequencestr transformstr'''
	# Rule for parsing a sequence of applied functions
	p[0] = utils.get_str_from_parsing(p)
		
def p_selectionstr(p):
	'''selectionstr : SIMPLESELECTOR STRING
					| SIMPLESELECTOR MULT
					| DEEPSELECTOR STRING
					| DEEPSELECTOR MULT
					| SIMPLESELECTOR filterliststr
					| conditionstr'''
	# Rule for parsing one a selection
	p[0] = utils.get_str_from_parsing(p)

def p_filterliststr(p):
	'''filterliststr : LSQUAREPAREN int RSQUAREPAREN
					 | LSQUAREPAREN indexesstr RSQUAREPAREN
					 | LSQUAREPAREN slicestr RSQUAREPAREN'''
	# Rule for parsing a filtering of list
	p[0] = utils.get_str_from_parsing(p)
	
def p_transformstr(p):
	'''transformstr : SIMPLESELECTOR FUNCNAME LPAREN RPAREN
					| SIMPLESELECTOR FUNCNAME LPAREN parametersstr RPAREN'''
	# Rule for parsing JPath function
	p[0] = utils.get_str_from_parsing(p)
		
def p_parametersstr_one(p):
	'''parametersstr : STRING
					 | int
					 | float'''
	# Rule for parsing available data types of function arguments
	p[0] = utils.get_str_from_parsing(p)
		
def p_parametersstr_group(p):
	'''parametersstr : parametersstr DELIMPARAMS parametersstr'''
	# Rule for parsing a list of arguments
	p[0] = utils.get_str_from_parsing(p)
		
def p_conditionstr(p):
	'''conditionstr : LSQUAREPAREN expressionstr RSQUAREPAREN
					| LSQUAREPAREN indexesstr RSQUAREPAREN
					| LSQUAREPAREN slicestr RSQUAREPAREN
					| LSQUAREPAREN MULT RSQUAREPAREN'''
	# Rule for parsing a filtering expression
	p[0] = utils.get_str_from_parsing(p)
	
def p_indexes(p):
	'''indexesstr : INT DELIMPARAMS INT
				  | indexesstr DELIMPARAMS INT'''
	# Rule for parsing a list of indexes
	p[0] = utils.get_str_from_parsing(p)
	
def p_slicestr(p):
	'''slicestr : SLICE
				| int SLICE
				| SLICE int
				| int SLICE int
				| slicestr SLICE
				| slicestr SLICE int'''
	# Rule for parsing a slice expression
	p[0] = utils.get_str_from_parsing(p)
	
def p_expressionstr_jpath(p):
	'''expressionstr : number
					 | FALSE
					 | TRUE
					 | NULL
					 | STRING
					 | jpathexprstr'''
	# Rule for parsing operands which can be used in a filtering expression
	p[0] = utils.get_str_from_parsing(p)

def p_expressionstr_uminus(p):
	'''expressionstr : MINUS expressionstr %prec UMINUS'''
	# Rule for parsing the operation unary minus
	p[0] = utils.get_str_from_parsing(p)
	
def p_expressionstr_math(p):
	'''expressionstr : expressionstr PLUS expressionstr
					 | expressionstr MINUS expressionstr
					 | expressionstr MULT expressionstr
					 | expressionstr DIV expressionstr
					 | expressionstr MOD expressionstr'''
	# Rule for parsing an arithmetic operations
	p[0] = utils.get_str_from_parsing(p)
	
def p_expressionstr_group(p):
	'''expressionstr : LPAREN expressionstr RPAREN'''
	# Rule for parsing a grouping of operations
	p[0] = utils.get_str_from_parsing(p)
	
def p_expressionstr_comp(p):
	'''expressionstr : expressionstr EQ expressionstr
					 | expressionstr NE expressionstr
					 | expressionstr LT expressionstr
					 | expressionstr LE expressionstr
					 | expressionstr GT expressionstr
					 | expressionstr GE expressionstr'''
	# Rule for parsing a comparation operations
	p[0] = utils.get_str_from_parsing(p)
	
def p_expressionstr_logic(p):
	'''expressionstr : expressionstr AND expressionstr
					 | expressionstr OR expressionstr'''
	# Rule for parsing a logical operations
	p[0] = p[1] + ' ' + p[2] + ' ' + p[3]

def p_int(p):
	'''int : INT
		   | MINUS INT'''
	# Rule for parsing positive and negative integers
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = -p[2]
		
def p_float(p):
	'''float : FLOAT
			 | MINUS FLOAT'''
	# Rule for parsing positive and negative float numbers
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = -p[2]
	
def p_number(p):
	'''number : INT
			  | FLOAT'''
	# Rule for parsing numbers
	p[0] = p[1]
	
# Define error rule
def p_error(t):
	if t == None:
		raise utils.JPSyntaxError('Unexpected end of JPath query')
	else:
		raise utils.JPSyntaxError('Unexpected token "' + str(t.value) + '"', t.lineno, t.lexpos)