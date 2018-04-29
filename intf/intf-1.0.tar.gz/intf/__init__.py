"""``intf`` provides a simple base class for integers with specified
default formatting. Define your own subclasses derived from `BaseIntF`
and specify desired formatting right with the class name. Decimal,
binary, octal and hexadecimal formats are supported. See `BaseIntF` for
more details.

Example::

    from intf import BaseIntF

    class int_04X(BaseIntF):
        pass

    x = int_04X(123)
    print '{}'.format(x)  # prints 0x007B

    class int_06o(BaseIntF):
        pass

    y = int_06o(123)
    print '{}'.format(y)  # prints 0o000173

    class int_08b(BaseIntF):
        pass

    z = int_08b(123)
    print '{}'.format(z)  # prints 0b01111011

    print '{:02x}'.format(z)  # still prints 7b

"""


import re


class _MetaIntF(type):
    """Metaclass for subclasses of `BaseIntF`.

    This metaclass creates specialized subclasses with desired integer
    formatting. Its main duty is to parse the class name, extract the
    format specification and put it into the class being created.
    """

    def __new__(cls, name, bases, dict_):
        if name != _MetaIntF._base_class_name:
            res = _MetaIntF._class_name_template.match(name)
            if res is None:
                syntax_error = SyntaxError(
                    "invalid name '%s' for a class derived from '%s'"
                    % (name, _MetaIntF._base_class_name))
                raise syntax_error
            dict_['_format_spec'] = res.group('format_spec')
            base_spec = res.group('pres_type').lower()
            dict_['_base_prefix'] = '0' + base_spec if base_spec != 'd' else ''
        else:
            dict_['_format_spec'] = ''
            dict_['_base_prefix'] = ''
        return type.__new__(cls, name, bases, dict_)

    _base_class_name = 'BaseIntF'

    _class_name_template = re.compile(
        r"^int_(?P<format_spec>(?:0[1-9][0-9]*)?(?P<pres_type>[dboxX]))$")


class BaseIntF(int):
    """Base class for integers with specified default formatting.

    When `str.format` is called on a string with replacement field which
    does not define ``format_spec`` explicitly, the default formatting
    for `int` argument is ``"{:d}"``. This default behavior cannot be
    changed by ordinary means as soon as the built-in `int` class and
    its instances prohibit modification of their fields and methods. So,
    when specific formatting like ``"0x{:04X}"`` or another is desired
    for particular variables, it must be specified explicitly in the
    replacement field.

    However, in some cases it might be very useful to bind specific
    formatting to particular variable and use it implicitly everywhere
    when such variable is printed, logged, etc. instead of specifying
    the same format multiple times in distant places. At least it helps
    to avoid potential inconsistency between points of use and bugs in
    specifying formatting codes, eliminate unnecessary copy-paste and
    abstract the code from insignificant details.

    To use this feature simply define an empty subclass based on this
    one and name your derived class according to the following template:
    ``^int_(0[1-9][0-9]*)?[dboxX]$``. The second part of the class name
    (the one after ``'_'`` delimiter) will define the default formatting
    of integer values that are instances of that class:
    * the trailing character denotes presentation type: decimal, binary,
        octal, and hexadecimal using lower- or upper-case letters. For
        all types except decimal the output is prepended with the base
        prefix: ``'0b'``, ``'0o'``, ``'0x'``
    * the preceding number specifies minimum field width if given. Note
        that base prefix such as ``'0x'`` does not consume the width
    * the first zero symbol instructs formatter to use zero as the fill
        character to pad the field to the whole width. Currently only
        zero is allowed, so it must be put if field width is given

    Example::

        class int_04X(BaseIntF):
            pass

        x = int_04X(123)
        print '{}'.format(x)  # prints 0x007B

    This is roughly equivalent to::

        x = 123
        print '0x{:04X}'.format(x)

    Note that different (nondefault) formatting still may be used also::

        x = int_04X(123)
        print '{:08b}'.format(x)  # prints 0b01111011

    .. note::

        This class should not be used directly. Derive subclasses with
        specific formatting as described above.

    .. warning::

        Arithmetic operations over this class are possible as for `int`
        but the result will have the pure `int` type, so the formatting
        from the argument is not inherited by the result.

    """

    __metaclass__ = _MetaIntF

    def __format__(self, format_spec):
        """Format this integer object.

        :arg str format_spec: forces the format if given, otherwise
            the default formatting specific to this class is used
        :returns: string with formatted representation of integer value

        """

        if not format_spec:
            return self._base_prefix + int.__format__(self, self._format_spec)
        return int.__format__(self, format_spec)
