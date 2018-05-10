import re

from lazyutils import delegate_to, lazy

ReType = type(re.compile('regex'))


class Regex:
    """
    A high level OO interface to regular expressions.
    """

    findall = delegate_to('regex')
    finditer = delegate_to('regex')
    fullmatch = delegate_to('regex')
    groupindex = delegate_to('regex')
    groups = delegate_to('regex')
    match = delegate_to('regex')
    scanner = delegate_to('regex')
    search = delegate_to('regex')
    split = delegate_to('regex')
    sub = delegate_to('regex')
    subn = delegate_to('regex')

    @lazy
    def regex(self):
        try:
            return re.compile(self.pattern, flags=self.flags)
        except RuntimeError:
            data = repr(self.pattern).replace(r'\\', '\\')
            raise ValueError('invalid regex: r%s' % data)

    @classmethod
    def from_groups(cls, *args, **kwargs):
        r"""
        Composes several different regular expressions into a grouped regex
        that identify the matches into the given groups.

        Args:
            args:
                A sequence of (name, re) pairs.
            kwargs:
                Keyword argumenst are of the form group_name=regex.

        Returns:
            A Regex object.

        Usage:
            Say we want to match integers vs float numbers:

            >>> integers = Regex(r'\d+')
            >>> floats = Regex(r'\d+\.\d*')
            >>> number = Regex.from_groups(('INTEGER', integers), ('FLOAT', floats))
            >>> number.match('42')
            <...>
        """
        items = [as_regex(y).in_group(x) for (x, y) in args]
        items.extend(as_regex(v).in_group(k) for k, v in kwargs.items())
        return cls('|'.join(regex.pattern for regex in items))

    @classmethod
    def safe(cls, st, **kwargs):
        """
        Create a Regex that matches the given string. Differently from the
        regular constructor, this constructor escapes all special characters.
        """
        return cls(re.escape(st), **kwargs)

    @classmethod
    def chars(cls, chars, negate=False, **kwargs):
        """
        Create a regex that matches any of the given sequence of characters.

        If negate=True, it matches the complement of the given characters.
        """
        data = ''.join(chars)
        if negate:
            return cls('[^%s]' % data)
        else:
            return cls('[%s]' % data)

    def __init__(self, pattern, flags=0, lazy=False):
        if isinstance(pattern, Regex):
            pattern = pattern.pattern

        self.pattern = pattern
        self.flags = flags
        if not lazy:
            # touches the lazy constructor
            self.regex = self.regex

    def __repr__(self):
        data = 'r' + repr(self.pattern).replace(r'\\', '\\')
        return '%s(%s)' % (self.__class__.__name__, data)

    def __str__(self):
        return self.pattern

    def __or__(self, other):
        if isinstance(other, Regex):
            return Regex('%s|%s' % (self.pattern, other.pattern))
        elif isinstance(other, str):
            return self | Regex.safe(other)
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, str):
            return Regex.safe(other) | self
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, Regex):
            patterns = (self.pattern, other.pattern)
            patterns = map(wrap_unsafe_or_pattern, patterns)
            return Regex(''.join(patterns))
        elif isinstance(other, str):
            return self + Regex.safe(other)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return Regex.safe(other) + self
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Regex):
            return self.pattern == other.pattern
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, int):
            data = wrap_unsafe_or_pattern(self.pattern)
            return Regex(data * other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    #
    # Public API
    #
    def is_fullmatch(self, string: str):
        """
        Return True if regular expression is a whole string match to the input
        string.
        """
        return self.regex.fullmatch(string) is not None

    def is_match(self, string: str):
        """
        Return True if string starts with a match for the regular expression.
        """
        return self.regex.match(string) is not None

    def is_in(self, string: str):
        """
        Return True if regular expression matches a sub-string of the given
        input.
        """
        return self.regex.search(string) is not None

    #
    # High level regex combinators
    #
    def optional(self):
        """
        Return an optional variant of the regular expression.
        """
        return Regex(wrap_for_repetition(self.pattern) + '?')

    def repeat(self, *args):
        """
        Matches repetitions of the base regular expression. This method
        can specify many different ways in which repetitions are allowed.

        regex.repeat():
            One or more repetitions.
        regex.repeat(...):
            Zero or more repetitions.
        regex.repeat(n):
            Exactly n repetitions.
        regex.repeat(n, ...):
            n or more repetitions.
        regex.repeat(m, n):
            Between n and m repetitions. If m < n, it does the standard greedy
            match, otherwise it tries to match the smaller possible number
            of repetitions.

        Note:
            The ellipsis (...) is a valid Python literal. So take the ellipsis
            literally in the examples above
        """
        if len(args) == 0:
            suffix = '+'
        elif len(args) == 1:
            n, = args
            if n is Ellipsis:
                suffix = '*'
            else:
                suffix = '{%d}' % n
        else:
            suffix = repetition_suffix(*args)
        return Regex(wrap_for_repetition(self.pattern) + suffix)

    def in_group(self, name=None, non_matching=False):
        """
        Wraps regular expression in a matching group. An optional name can be
        given in order to refer to the group by name (recommended) rather than
        by location.

        Args:
            name:
                Optional name of the group.
            non_matching (bool):
                If True, wraps in a non-matching group.
        """

        if non_matching:
            return Regex('(?:%s)' % self.pattern)
        elif name is None:
            return Regex('(%s)' % self.pattern)
        else:
            return Regex('(?P<%s>%s)' % (name, self.pattern))

    def ref(self, name):
        """
        Adds a back reference to a named group in the end of the group.
        """
        if isinstance(name, int):
            if not (0 < name < 100):
                raise ValueError('numbered groups must be on the (0, 99) range')
            data = r'\%i' % name
        else:
            data = r'(?P=%s)' % name
        return Regex(self.pattern + data)

    def look_ahead(self, pattern, negative=False):
        """
        Matches only if the given pattern is present ahead of the current
        selection.
        """
        if isinstance(pattern, str):
            pattern = Regex.safe(pattern)
        if negative:
            data = r'(?!%s)' % pattern.pattern
        else:
            data = r'(?=%s)' % pattern.pattern
        return Regex(self.pattern + data)

    def look_behind(self, pattern, negative=False):
        """
        Matches only if the given pattern is present behind of the current
        selection.
        """
        if isinstance(pattern, str):
            pattern = Regex.safe(pattern)
        if negative:
            data = r'(?<!%s)' % pattern.pattern
        else:
            data = r'(?<=%s)' % pattern.pattern
        return Regex(data + self.pattern)

    def if_group(self, name, yes_pattern, no_pattern):
        """
        Matches if group with the given name or index exists in the current
        regex.

        Args:
            name:
                Name or 1-index of the requested group.
            yes_pattern:
                The pattern to use if group exists.
            no_pattern:
                The pattern to use if group does not exit
        """
        fmt = '(?({name}){yes}|{no})'
        yes_pattern = as_regex(yes_pattern)
        no_pattern = as_regex(no_pattern)
        return Regex(self.pattern + fmt.format(
            name=str(name),
            yes=wrap_unsafe_or_pattern(yes_pattern.pattern),
            no=wrap_unsafe_or_pattern(no_pattern.pattern),
        ))


def as_regex(obj, safe=True):
    """
    Coerce input to a Regex instance.
    """
    if isinstance(obj, Regex):
        return obj
    elif isinstance(obj, str):
        if safe:
            return Regex.safe(obj)
        else:
            return Regex(obj)
    elif isinstance(obj, ReType):
        regex = Regex(obj.pattern, lazy=True)
        regex.regex = obj
        return regex
    else:
        raise TypeError('could not convert to Regex')


def wrap_unsafe_or_pattern(pattern):
    """
    Wraps any pattern that contains an unsafe or operator inside an (?:...)
    """
    if '|' in pattern:
        return '(?:%s)' % pattern
    else:
        return pattern


def wrap_for_repetition(pattern):
    """
    Wrap pattern into (?:...) group if it is not safe to use with a repetition
    operator.
    """
    if len(pattern) <= 1:
        return pattern
    elif pattern in SAFE_PATTERNS:
        return pattern

    ends = pattern[0], pattern[-1]
    if ends == ('[', ']') and pattern.count(']') == 1:
        return pattern
    elif ends == ('(', ')') and pattern.count(')') == 1:
        return pattern
    else:
        return '(?:%s)' % pattern


def repetition_suffix(m, n):
    if n is Ellipsis:
        if m == 0:
            suffix = '*'
        elif m == 1:
            suffix = '+'
        else:
            suffix = '{%d,}' % m
    elif m <= n:
        if m == 0 and n == 1:
            suffix = '?'
        else:
            suffix = '{%d,%d}' % (m, n)
    else:
        suffix = '{%d,%d}?' % (n, m)
    return suffix


SAFE_PATTERNS = {
    r'.', r'\.', '^', r'\^', r'$', r'\$', r'\\',
    r'\A', r'\Z', r'\d', r'\D', r'\s', r'\S', r'w', r'\W', r'\b', r'\B',
    r'\(', r'\)', r'\[', r'\]', r'\{', r'\}',
    r'\*', r'\+', r'\-', r'\|',
}
