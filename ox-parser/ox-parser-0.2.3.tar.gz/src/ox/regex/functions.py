import functools
import re

from .regex import Regex


def regex_method(method):
    """
    Creates a new toplevel function from the given regex method.
    """

    @functools.wraps(method)
    def function(st, *args, **kwargs):
        return method(Regex(st), *args, **kwargs)

    return function


# (we don't inject stuff at globals() to make static analyzers happy)
safe = Regex.safe
chars = Regex.chars
grouped = Regex.from_groups

# Re module API
findall = regex_method(Regex.findall)
finditer = regex_method(Regex.finditer)
fullmatch = regex_method(Regex.fullmatch)
groupindex = regex_method(Regex.groupindex)
groups = regex_method(Regex.groups)
match = regex_method(Regex.match)
scanner = regex_method(Regex.scanner)
search = regex_method(Regex.search)
split = regex_method(Regex.split)
sub = regex_method(Regex.sub)
subn = regex_method(Regex.subn)


def pattern(regex):
    """
    Return the raw string pattern of a Regex instance.
    """
    return regex.pattern


# Other methods
optional = regex_method(Regex.optional)
repeat = regex_method(Regex.repeat)
group = regex_method(Regex.in_group)
ref = regex_method(Regex.ref)
look_ahead = regex_method(Regex.look_ahead)
look_behind = regex_method(Regex.look_behind)
if_group = regex_method(Regex.if_group)


#
# Utilities
#
def make_enclosing_regex(open: str, close: str):
    """
    Creates regular expression that captures any text wrapped between the
    opening and closing values.

    Examples:

        >>> regex = make_enclosing_regex('[', ']')
        >>> regex.is_fullmatch('[foo]')
        True
        >>> regex.is_fullmatch('foo')
        False
    """

    regex = [re.escape(open)]
    regex.append('(?:[^' + re.escape(close[0]) + ']*')
    if len(close) == 1:
        regex.append(')')
    else:
        acc = re.escape(close[0])
        for x in close[1:]:
            x_ = re.escape(x)
            regex.append(acc + '[^%s]' % x_)
            acc += x_
        regex.append(')+')
    regex.append(re.escape(close))
    return Regex(''.join(regex))
