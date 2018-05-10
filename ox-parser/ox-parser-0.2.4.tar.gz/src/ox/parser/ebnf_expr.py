from string import ascii_letters

from sidekick import Union, opt
from .utils import is_word, memo_dict
from ..helpers import identity, singleton, cons


class Expr(Union):
    """
    Represents an AST node of a EBNF expression.
    """

    is_atom = False
    is_list = False

    def to_token(self, memo):
        """
        Replace all Literal's with a Token expression.

        The mapping between literal values and token expressions is stored in
        the memo dictionary.
        """

        if self.is_atom:
            return self
        elif self.is_list:
            cls = type(self)
            return cls([x.to_token(memo) for x in self.data])
        else:
            cls = type(self)
            args = (x.to_token(memo) for x in self.args)
            return cls(*args)

    def to_simple(self, name, handler, memo):
        """
        Extract all complex rules from the given (name, handler) pair.

        Args:
            name:
                Name assigned to the expression.
            handler:
                The handler function responsible for processing nodes for
                the given expression.
            memo :
                A set of production names that is used to avoid repeated
                productions.

        Returns:
            A sequence of pairs of (name, expr) of simple expressions.
        """
        yield (name, self, handler)

    def source(self):
        """
        Renders source code for expression.
        """
        return str(self.args[0])

    def normalize_names(self):
        """
        Replace all Literal's with a Token expression.

        The mapping between literal values and token expressions is stored in
        the memo dictionary.
        """

        if self.is_name:
            return Name(self.value)
        elif self.is_atom:
            return self
        elif self.is_list:
            cls = type(self)
            return cls([x.normalize_names() for x in self.data])
        else:
            cls = type(self)
            args = (x.normalize_names() for x in self.args)
            return cls(*args)


# --- Atoms ----------------------------------------------------------------
class Name(Expr):
    is_atom = True
    is_simple = True
    args = opt(str)


class Token(Expr):
    is_atom = True
    is_simple = True
    args = opt(str)


class Literal(Expr):
    is_atom = True
    is_simple = False
    args = opt(str)

    def to_token(self, memo):
        data = self.value
        try:
            value = memo[data]
        except KeyError:
            try:
                tk_name = memo_dict[data]
            except KeyError:
                if is_word(data):
                    tk_name = '%s_' % data.upper()
                else:
                    tk_name = 'TK_SYMB_%s_' % (len(memo) + 1)
            memo[data] = tk_name
            value = tk_name
        return Token(value)

    def to_simple(self, name, handler, memo):
        token = self.to_token({})
        yield (name, token, handler)


#
# Expression modifiers
#
class Optional(Expr):
    is_simple = False
    args = opt(Union)

    def to_simple(self, name, handler, memo):
        yield (name, Name('empty'), lambda *_: handler(None))
        yield from self.value.to_simple(name, handler, memo)

    def source(self):
        return '[%s]' % self.value.source()


class Hidden(Expr):
    is_simple = True
    args = opt(Union)

    def to_simple(self, name, handler, memo):
        value = self.value

        if value.is_name or value.is_token:
            yield (name, self, handler)
        elif value.is_literal:
            token = value.to_token({})
            yield (name, token, handler)
        else:
            hidden_name = name + '_hidden'
            yield (name, Name(hidden_name), handler)
            yield from value.to_simple(hidden_name, identity)

    def source(self):
        if self.value.is_hidden:
            return self.value.value.source()
        return '~' + self.value.source()


class Repeat(Expr):
    is_simple = False
    args = opt(Union)

    def to_simple(self, name, handler, memo):
        yield from to_simple_repeat(self, name, handler, memo, True, 'STAR')


class RepeatOne(Expr):
    is_simple = False
    args = opt(Union)

    def to_simple(self, name, handler, memo):
        yield from to_simple_repeat(self, name, handler, memo, False, 'PLUS')


#
# Container expressions
#
class Or(Expr):
    is_simple = property(lambda self: all(x.is_simple for x in self.data))

    is_list = True
    args = opt(data=list)

    def to_simple(self, name, handler, memo):
        for obj in self.data:
            yield from obj.to_simple(name, handler, memo)

    def source(self):
        return ' | '.join(x.source() for x in self.data)


class Sequence(Expr):
    is_list = True
    is_simple = property(lambda self: all(x.is_simple for x in self.data))
    args = opt(data=list)

    def to_simple(self, name, handler, memo):
        items = []
        extra = []
        for i, part in enumerate(self.data, start=1):
            part_name = '%s_X%s' % (name, i)
            expansions = list(part.to_simple(part_name, identity, memo))

            if len(expansions) == 1 and expansions[0][1] == part:
                items.append(part)
            else:
                items.append(Name(part_name))
                extra.extend(expansions)

        yield (name, Sequence(items), handler)
        yield from extra

    def source(self):
        return ' '.join(x.source() for x in self.data)


def to_simple_repeat(expr, name, handler, memo, has_empty, suffix):
    """
    Common implementation of to_simple to Repeat and RepeatOne
    """
    seq_name = new_unique_name('%s_%s' % (name, suffix), memo)
    seq_name_var = Name(seq_name)

    yield (name, Name(seq_name), handler)
    if has_empty:
        yield (seq_name, Name('empty'), lambda *_: [])
    for (name_, expr, _) in expr.value.to_simple(seq_name, None, memo):
        yield (name_, expr, singleton)
        yield (name_, Sequence([expr, seq_name_var]), cons)


def new_unique_name(name, memo):
    """
    Return a new unique name considering the memo names set.
    """

    base = name
    if base not in memo:
        return base
    for letter in ascii_letters:
        name = base + letter
        if name not in memo:
            return name
    raise ValueError('could not find a valid name replacement for %r' % base)
