import re
from collections import OrderedDict, Counter

from lazyutils import lazy
from sidekick import Record, field, record
from .utils import full_regex, match_any, ply_lexer_error, from_reserved_name
from .utils import is_reserved, is_ignored, is_token_name
from ..regex import as_regex


class LexerMeta(type):
    """
    Metaclass for lexer objects.
    """

    def __new__(meta, name, bases, namespace):  # noqa: N804
        return super().__new__(meta, name, bases, dict(namespace))

    def __init__(cls, name, bases, namespace):  # noqa: N805
        cls.tokens = OrderedDict()
        cls.ignored = OrderedDict()
        cls.reserved = {}

        # Fill the tokens, ignored dictionaries and the reserved set.
        cls._fill_meta_info_dicts()

        # Create list with all token names
        cls.token_names = list(cls.tokens)
        cls.token_names.extend(cls.reserved)

        # Check if any rule matches whitespace
        cls.match_space = match_any(cls.tokens.values(), ' ')
        cls.match_newline = match_any(cls.tokens.values(), '\n')
        cls.match_tab = match_any(cls.tokens.values(), '\t')
        cls.match_whitespace = cls.match_space or cls.match_newline or cls.match_tab

        # Check if reserved keywords should indeed be reserved (i.e., they must
        # match another rule and map be reserved as an special token in the
        # final token stream).
        cls._check_reserved_words()

        # Creates the full match rule
        whitespace_re = ''
        rules = cls.tokens.copy()
        if not cls.match_newline:
            whitespace_re += '\n'
        if not cls.match_space:
            whitespace_re += ' '
        if not cls.match_tab:
            whitespace_re += '\t'

        if whitespace_re:
            whitespace_re = r'[%s]' % whitespace_re
            rules['whitespace'] = as_regex(whitespace_re, safe=False)
        rules['error'] = as_regex(r'.+', safe=False)
        cls.full_regex = full_regex(rules)

    def __prepare__(meta, bases):  # noqa: N805
        return OrderedDict()

    def _fill_meta_info_dicts(cls):  # noqa: N805
        # Fill the meta-info dictionaries
        tk_names = filter(is_token_name, dir(cls))
        for tk_name in tk_names:
            tk_def = getattr(cls, tk_name)

            if is_reserved(tk_name):
                tk_name = from_reserved_name(tk_name)
                cls.reserved[tk_name] = tk_def
            else:
                tk_def = as_regex(tk_def, safe=False)
                cls.tokens[tk_name] = tk_def
                if is_ignored(tk_name):
                    cls.ignored[tk_name] = tk_def

    def _check_reserved_words(cls):  # noqa: N805
        for name, word in cls.reserved.items():
            if not isinstance(word, str):
                msg = 'reserved words must be strings: %s = %r' % (name, word)
                raise ValueError(msg)
            if not match_any(cls.tokens.values(), word):
                re_expr = re.escape(word)
                raise RuntimeError(
                    'Token definition %s = %r is not be a reserved word since '
                    'it does not match any other definition. Please create a '
                    'new rule %s = r"%s" instead of declaring it reserved.'
                    % (name, word, name, re_expr)
                )
        if len(cls.reserved.values()) != len(cls.reserved):
            word, _ = Counter(cls.reserved.values()).most_common(1)
            w1, w2, *_ = (k for k, v in cls.reserved.items() if v == word)
            raise ValueError(
                'Repeated reserved keyword values: %s and %s' % (w1, w2)
            )


class Lexer(metaclass=LexerMeta):
    """
    Base class for all Ox lexers.
    """

    tokens = {}
    reserved = {}
    ignored = {}
    match_space = False
    match_newline = False
    match_tab = False
    match_whitespace = False
    full_regex = None

    def __init__(self, source, which='auto'):
        self.source = source
        self.which = which

    def __iter__(self):
        which = 'itertokens_' + self.which
        if self.which == 'auto' or self.which == 'simple':
            which = 'itertokens'
        try:
            method = getattr(self, which)
        except AttributeError:
            raise ValueError('invalid lexing method: %r' % self.which)
        return method()

    @classmethod
    def tokenize(cls, source, **kwargs):
        """
        Tokenize source code.
        """
        lexer = cls.make_lexer(**kwargs)
        return lexer(source)

    @classmethod
    def make_lexer(cls, which='auto', transform=lambda x: x, lazy=False):
        """
        Return a lexer function from the class definitions.
        """

        def lexer(source, lazy=lazy):
            if lazy:
                lex = cls(source, which=which)
                return (transform(tk) for tk in lex)
            else:
                return list(lexer(source, lazy=True))

        return lexer

    @lazy
    def _ply_lexer(self):
        from ply import lex

        # PLY documentation asks us to define a series of constants or
        # functions named as t_TOK_NAME in a module. This is not strictly
        # necessary and any introspectable Python object that exposes those
        # constants via getattr is good enough. We use a record() object here
        # and let PLY instrospect it by pretending it is a module :)
        namespace = {}
        namespace['tokens'] = self.token_names
        namespace['t_ignore'] = ' \t'
        namespace['t_error'] = ply_lexer_error

        for k, v in self.tokens.items():
            namespace['t_' + k] = v.pattern

        return lex.lex(module=record(**namespace))

    def itertokens(self, show_ignored=False):
        """
        Iterate over a list of tokens.
        """

        # List of ignored tokens
        if show_ignored:
            ignored = set()
        else:
            ignored = set(self.ignored)

        # List of reserved words
        reserved = {v: k for k, v in self.reserved.items()}

        for match in re.finditer(self.full_regex, self.source):
            typ = match.lastgroup
            value = match.group(typ)

            if typ == 'whitespace':
                continue
            elif typ in ignored:
                continue
            elif typ == 'error':
                raise SyntaxError('invalid value: %r' % value)

            typ = reserved.get(value, typ)
            yield Token(typ, value)

    def itertokens_ply(self):
        ply_lexer = self._ply_lexer
        ply_lexer.input(self.source)
        while True:
            tok = ply_lexer.token()
            if tok is None:
                break
            yield Token(tok.type, tok.value, tok.lineno, tok.lexpos, self)


class Token(Record):
    """
    Represents a token.

    Used internally by all lexers.
    """

    type = field()
    value = field()
    lineno = field(default=None)
    lexpos = field(default=None)
    lexer = field(default=None)

    def __repr__(self):
        return '%s(%r)' % (self.type, self.value)

    def __eq__(self, other):
        if type(other) is Token:
            return self.type == other.type and self.value == other.value
        return NotImplemented

    def copy(self, **kwargs):
        """
        Copy token possibly changing some of its attributes.

        >>> Token('NAME', 'foo').copy(value='bar')
        NAME('bar')
        """
        for attr in ('type', 'value', 'lineno', 'lexpos', 'lexer'):
            kwargs.setdefault(attr, getattr(self, attr))
        return Token(**kwargs)
