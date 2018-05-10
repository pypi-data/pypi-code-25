import re

TOKEN_NAME = re.compile(r'^(r_|reserved_|_)?[A-Z][A-Z0-9_]*$')
RESERVED = re.compile(r'^(r_|reserved_)[A-Z][A-Z0-9_]*$')


def full_regex(rules):
    """
    Create a full match regex from a dictionary of rules.
    """
    regex = '|'.join(r'(?P<%s>%s)' % (k, v.pattern) for (k, v) in rules.items())
    return re.compile(regex)


def match_any(rules, string):
    """
    Return True if matches any regex on the list.
    """
    return any(rule.fullmatch(string) for rule in rules)


def is_reserved(x):
    return bool(RESERVED.match(x))


def is_ignored(x):
    return getattr(x, 'pattern', x).startswith('_')


def is_token_name(args):
    return bool(TOKEN_NAME.match(args))


def from_reserved_name(tk_name):
    if tk_name.startswith('reserved_'):
        return tk_name[9:]
    else:
        return tk_name[2:]


def ply_lexer_error(lex):
    raise SyntaxError("Illegal character '%s'" % lex.value[0])
