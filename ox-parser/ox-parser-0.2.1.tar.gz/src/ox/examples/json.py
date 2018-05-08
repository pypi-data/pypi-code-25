import ox
from ox.helpers import identity, cons, clean_string, constant, pair


lexer = ox.make_lexer([
    ('STRING', r'"[^"]*"'),
    ('NUMBER', r'[0-9]+'),
    ('KEYWORD', r'true|false|null'),
    ('SYMBOLS', r'[[\]{},:]'),
])

parser = ox.make_parser([
    ("json : object | array | atom", identity),

    # Objects
    ("object : '{' [ pairs ]'}'", lambda x: dict(x) or {}),
    ("pairs  : pair (',' pair)*", cons),
    ("pair   : string ':' json", pair),

    # Arrays
    ("array : '[' [ items ] ']'", lambda x: x or []),
    ("items : json (',' json)*", cons),

    # Terminals
    ("string : STRING", clean_string),
    ("atom : NUMBER", float),
    ("atom : string", identity),
    ("atom : 'true'", constant(True)),
    ("atom : 'false'", constant(False)),
    ("atom : 'null'", constant(None)),
])

loads = lexer >> parser
