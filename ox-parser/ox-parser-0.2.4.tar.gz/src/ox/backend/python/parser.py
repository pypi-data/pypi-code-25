import operator
import tokenize

from ox.helpers import identity, constant
from ox.helpers import second, cons, pair
from ox.lexer import Lexer
from ox.parser import make_parser

operator_map = {
    '<': operator.lt,
}
get_operator = operator_map.get


class PythonLexer(Lexer):
    NEWLINE = r'\n'
    STRING = tokenize.String
    FLOAT = tokenize.Floatnumber
    ELLIPSIS = r'\.\.\.'

    # Comparison operators
    LT = r'<'
    LE = r'<='
    GE = r'>='
    GT = r'>'
    EQ = r'=='
    NE = r'!='
    # r_IN = 'in'
    # r_NOT = 'not'
    # r_IS = 'is'


#
# Grammar for Python -- grammar file extracted from Python36/Grammar/Grammar
# source tree.
#
grammar_rules = [

    # Decorators
    ("decorator  : '@' dotted_name [ '(' [arglist] ')' ] NEWLINE", ...),
    ("decorators : decorator+", ...),
    ("decorated  : decorators (classdef | funcdef | async_funcdef)", ...),

    # Function definition and arguments
    ("async_funcdef : ASYNC funcdef", ...),
    ("funcdef       : 'def' NAME parameters [ '->' test ] ':' suite", ...),
    ("parameters    : '(' [ typedargslist ] ')'", ...),

    ("typedargslist : ( targsfull | targsstars | tarkwargs ) [',']", identity),
    ("targsfull   : targsopt [ ',' targsstars ]", ...),
    ("targsopt    : tfpdefopt ( ',' tfpdefopt )*", cons),
    ("targsstars  : tfpstarargs [ ','tarkwargs ]", ...),
    ("tfpstarargs : '*' [ vfpdef ] ( ',' tfpdefopt )*", ...),
    ("tarkwargs   : '**' tfpdef", ...),
    ("tfpdefopt   : tfpdef ['=' test]", ...),
    ("tfpdef      : NAME [':' test]", ...),

    ("varargslist : ( vargsfull | vargsstars | varkwargs ) [',']", identity),
    ("vargsfull   : vargsopt [ ',' vargsstars ]", ...),
    ("vargsopt    : vfpdefopt ( ',' vfpdefopt )*", cons),
    ("vargsstars  : vfpstarargs [ ',' varkwargs ]", ...),
    ("vfpstarargs : '*' [ vfpdef ] ( ',' vfpdefopt )*", ...),
    ("varkwargs   : '**' vfpdef", ...),
    ("vfpdefopt   : vfpdef ['=' test]", ...),
    ("vfpdef      : NAME", ...),

    # Statement types
    ("stmt        : simple_stmt | compound_stmt", identity),
    ("simple_stmt : small_stmt ( ';' small_stmt )* [';'] ~NEWLINE", cons),
    ("small_stmt  : expr_stmt | del_stmt | pass_stmt | flow_stmt | import_stmt"
     "            | global_stmt | nonlocal_stmt | assert_stmt", ...),

    # Expr statement
    ("expr_stmt : testlist_star_expr annassign", ...),
    ("expr_stmt : augassign ( yield_expr | testlist )", ...),
    ("expr_stmt : ( '=' ( yield_expr | testlist_star_expr ) )*", ...),
    ("annassign : ':' test [ '=' test ]", ...),
    ("augassign : `+=` | `-=` | `*=` | `@=` | `/=` | `%=` | `&=` | `|=` "
     "          | `^=` | `<<=` | `>>=` | `**=` | `//=`", ...),
    ("testlist_star_expr : testlist_item ( ',' testlist_item )* [',']", cons),

    # Control flow
    ("flow_stmt     : break_stmt | continue_stmt | return_stmt | raise_stmt"
     "              | yield_stmt", identity),
    ("break_stmt    : 'break'", ...),
    ("continue_stmt : 'continue'", ...),
    ("return_stmt   : 'return' [ testlist ]", ...),
    ("yield_stmt    : yield_expr", ...),
    ("raise_stmt    : 'raise' [ test [ 'from' test ] ]", ...),
    ("pass_stmt     : 'pass'", ...),

    # Import statement
    ("import_stmt     : import_name | import_from", identity),
    ("import_name     : 'import' dotted_as_names", ...),
    ("import_from     : 'from' import_source 'import' import_dest", ...),
    ("import_source   : [dots] dotted_name", ...),
    ("import_source   : dots", ...),
    ("import_dest     : '*'", ...),
    ("import_dest     : '(' import_as_names ')' | import_as_names", ...),
    ("dots            : '.'+ | ELLIPSIS", ...),
    ("import_as_names : import_as_name ( ',' import_as_name )* [',']", cons),
    ("import_as_name  : NAME [ 'as' NAME ]", ...),
    ("dotted_as_names : dotted_as_name ( ',' dotted_as_name )*", cons),
    ("dotted_as_name  : dotted_name [ 'as' NAME ]", ...),
    ("dotted_name     : NAME ( '.' NAME )*", cons),

    # Other simple statements
    ("del_stmt      : 'del' exprlist", ...),
    ("global_stmt   : 'global' NAME ( ',' NAME )*", cons),
    ("nonlocal_stmt : 'nonlocal' NAME ( ',' NAME )*", cons),
    ("assert_stmt   : 'assert' test [ ',' test ]", cons),

    # Compound statements
    ("compound_stmt : if_stmt | while_stmt | for_stmt"
     "              | try_stmt | with_stmt | funcdef | classdef"
     "              | decorated | async_stmt", identity),
    ("async_stmt    : ASYNC ( funcdef | with_stmt | for_stmt )", second),

    ("if_stmt    :  if_block elif_block* [ else_block ]", ...),
    ("if_block   : 'if' test ':' suite", ...),
    ("elif_block : 'elif' test ':' suite", ...),
    ("else_block : 'else' ':' suite", ...),

    ("while_stmt  : while_block [ else_block ]", ...),
    ("while_block : 'while' test ':' suite", ...),

    ("for_stmt  : for_block [ else_block ]", ...),
    ("for_block : 'for' exprlist 'in' testlist ':' suite", ...),

    ("with_stmt : 'with' with_item ( ',' with_item )*  ':' suite", ...),
    ("with_item : test [ 'as'  expr ]", ...),

    ("try_stmt      : try_block ( except_block )* [ else_block ] "
     "                [ finally_block ]", ...),
    ("try_block     : 'try' ':' suite", ...),
    ("except_block  : except_clause ':' suite", ...),
    ("finally_block : except_clause ':' suite", ...),
    ("except_clause : 'except' [ test [ 'as' NAME ] ]", ...),

    ("suite : simple_stmt", ...),
    ("suite : NEWLINE INDENT stmt+ DEDENT", ...),

    # Expression (test) types
    ("test : or_test 'if' or_test 'else' test", ...),
    ("test : lambdef", ...),
    ("test : or_test", identity),

    # Lambda expressions
    ("lambdef        : 'lambda' [ varargslist ] ':' test", ...),
    ("lambdef_nocond : 'lambda' [ varargslist ] ':' test_nocond", ...),
    ("test_nocond    : or_test | lambdef_nocond", ...),

    # Short-circuit logic expressions
    ("or_test  : and_test ( 'or' and_test )*", ...),
    ("and_test : not_test ( 'and' not_test )*", ...),
    ("not_test : 'not' not_test", ...),
    ("not_test : comparison", identity),

    # Comparison
    ("comparison : expr ( comp_op expr )*", ...),
    ("comp_op    : `<` | `>` | `<=` | `>=` | `==` | `!=`", get_operator),
    ("comp_op    : 'in'", lambda: (lambda x, y: x not in y)),
    ("comp_op    : 'not' 'in'", lambda: (lambda x, y: x not in y)),
    ("comp_op    : 'is'", constant(operator.is_)),
    ("comp_op    : 'is' 'not'", constant(operator.is_not)),

    # Logical/arithmetical and shift operations
    ("expr       : xor_expr ( '|' xor_expr )*", ...),
    ("xor_expr   : and_expr ( '^' and_expr )*", ...),
    ("and_expr   : shift_expr ( '&' shift_expr )*", ...),
    ("shift_expr : arith_expr ( shift_op arith_expr )*", ...),
    ("arith_expr : term ( plus_op term )*", ...),
    ("term       : factor ( mul_op factor )*", ...),
    ("factor     : unary_op factor", ...),
    ("factor     : power", ...),
    ("power      : atom_expr [ '**' factor ]", ...),

    # Operator groups
    ("shift_op : `<<` | `>>`", get_operator),
    ("plus_op  : `+` | `-`", get_operator),
    ("mul_op   : `*` | `@` | `/` | `%` | `//`", get_operator),
    ("unary_op : `+` | `-` | `~`", get_operator),

    # Atoms
    ("atom_expr : [AWAIT] atom trailer*", ...),
    (
        "atom       : NAME | NUMBER | STRING+ | singleton | container"
        "           | comprehension", ...),
    ("atom      : '(' yield_expr ')'", identity),
    ("singleton : '...'", constant(...)),
    ("singleton : 'None'", constant(None)),
    ("singleton : 'True'", constant(True)),
    ("singleton : 'False'", constant(False)),

    # Container types
    ("container : tuple | list | dict | set", ...),
    ("tuple     : '(' [ testlist_items ] ')'", ...),
    ("list      : '[' [ testlist_items ] ']'", ...),
    ("set       : '{' testlist_items '}'", ...),
    ("dict      : '{' [ dict_items ] '}'", ...),

    ("testlist_items : testlist_item ( ',' testlist_item )* [',']", cons),
    ("testlist_item  : test | star_expr", identity),
    ("star_expr      : '*' expr", ...),

    ("dict_items : dict_item ( ',' dict_item )* [',']", cons),
    ("dict_item  : pair | '**' expr", identity),
    ("pair       : test ':' test", pair),

    # Comprehensions
    ("comprehension : tuple_comp | list_comp | set_comp | dict_comp", ...),
    ("tuple_comp    : '(' test comp_for ')'", ...),
    ("list_comp     : '[' test comp_for ']'", ...),
    ("set_comp      : '{' test comp_for '}'", ...),
    ("dict_comp     : '{' pair comp_for '}'", ...),
    ("comp_for      : [ASYNC] 'for' exprlist 'in' or_test [comp_iter]", ...),
    ("comp_if       : 'if' test_nocond [comp_iter]", ...),
    ("comp_iter     : comp_for | comp_if", identity),

    # Atom trailer (function calls, attribute access or subscripts)
    ("trailer       : '(' [arglist] ')'", ...),
    ("trailer       : '[' subscriptlist ']'", ...),
    ("trailer       : '.' NAME", ...),
    ("subscriptlist : subscript ( ',' subscript )* [',']", ...),
    ("subscript     : test", ...),
    ("subscript     : [test] ':' [test] [sliceop]", ...),
    ("sliceop       : ':' [test]", ...),

    # Special sequences
    ("exprlist      : exprlist_item ( ',' exprlist_item )* [',']", cons),
    ("exprlist_item : expr | star_expr", identity),
    ("testlist      : test (',' test)* [',']", ...),

    # Class and arguments
    #
    # The reason that keywords are test nodes instead of NAME is that using NAME
    # results in an ambiguity. ast.c makes sure it's a NAME.
    # "test '=' test" is really "keyword '=' test", but we have no such token.
    # These need to be in a single rule to avoid grammar that is ambiguous
    # to our LL(1) parser. Even though 'test' includes '*expr' in star_expr,
    # we explicitly match '*' here, too, to give it proper precedence.
    # Illegal combinations and orderings are blocked in ast.c:
    # multiple (test comp_for) arguments are blocked; keyword unpackings
    # that precede iterable unpackings are blocked; etc.
    ("classdef : 'class' NAME [ '(' [ arglist ] ')' ] ':' suite", ...),
    ("arglist  : argument ( ',' argument )*  [',']", cons),
    ("argument : test [ comp_for ]", ...),
    ("argument : test '=' test", ...),
    ("argument : '**' test", ...),
    ("argument : '*' test", ...),

    # Generator expressions
    ("yield_expr : 'yield' [yield_arg]", ...),
    ("yield_arg  : 'from' test", ...),
    ("yield_arg  : testlist", ...),

    # not used in grammar, but may appear in "node" passed from Parser to
    # Compiler
    # ("encoding_decl: NAME", ...),
]

#
# Start symbols for the grammar:
#       single_input is a single interactive statement;
#       file_input is a module or sequence of commands read from an input file;
#       eval_input is the input for the eval() functions.
# NB: compound_stmt in single_input is followed by extra NEWLINE!
#

# Single input
single_input_rules = [
    ("single_input : NEWLINE | simple_stmt | compound_stmt ~NEWLINE", ...),
]
single_input_rules.extend(grammar_rules)
single_input_parser = make_parser(single_input_rules, which='ebnf')

# File input
file_input_rules = [
    ("file_input : ( NEWLINE | stmt )* ~ENDMARKER", ...),
]
file_input_rules.extend(grammar_rules)
file_input_parser = make_parser(file_input_rules, which='ebnf')

# Eval input
eval_input_rules = [
    ("eval_input : testlist NEWLINE* ~ENDMARKER", ...),
]
eval_input_rules.extend(grammar_rules)
eval_input_parser = make_parser(eval_input_rules, which='ebnf')
