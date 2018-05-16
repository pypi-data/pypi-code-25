"""This package defines two classes:

* `subrange` -- continuous subrange of integers as a ``min..max`` object

* `subrangef` -- annotated `subrange` with reach formatting capabilities

If you are new to this package, start with the `subrange`. It implements
the core features of subranges::

    from subrange import subrange

    r = subrange(1, 5)          # subrange of integers 1..5

    print r                     # 1..5
    print r.min, r.max          # 1 5
    print repr(r)               # subrange(1, 5)
    print "{:04b}".format(r)    # 0001..0101
    print 4 in r                # True
    print [i for i in r]        # [1, 2, 3, 4, 5]
    print r < 6                 # True

If you need annotated subranges with reach formatting, consider using
`subrangef`::

    from subrange import subrangef

    f = subrangef(0, 127,
                  str_spec="0x{value:02X} {id!r}",  # format string
                  id="ASCII_CHARSET",               # annotation
                  brief="ASCII character codes")    # annotation

    print f     # 0x00..7F 'ASCII_CHARSET'

    print "{brief}: {min} to {max}".format(**f.__dict__)
    # ASCII character codes: 0 to 127

Subrange instances are immutable hashable ordered collections of unique
integers in the range from ``min`` to ``max`` inclusively.

Annotated subranges are initialized with custom set of attributes (those
are ``id`` and ``brief`` in the example above, but it may be almost
arbitrary set of attributes) and a format string ``str_spec`` that
defines the default formatting of the created instance.

Much more detailed description with examples may be found in
documentation to `subrange` and `subrangef` classes.
"""


class subrange(object):
    """Continuous subrange of integers as a ``min..max`` object.

    Instances of this class are immutable hashable ordered collections
    of unique integers in the range from ``min`` to ``max`` inclusively.

    New instances are normally created provided two integer values
    ``min`` and ``max`` that define limits of subrange as ``min..max``.

    See documentation on methods for more details.
    """

    def __new__(cls, *args):
        """Create and initialize a new instance of `subrange`.

        :arg tuple args: couple of integers or a complex initializer
        :returns: newly created and initialized instance of `subrange`

        Parameter ``args`` defines limits of subrange as ``min..max``.
        Limits must be integers. Subranges based on different ordinal
        data types are not supported. The simplest way is to pass a
        couple of integers with ``args``. The first one is treated as
        ``min`` and the second as ``max``::

            subrange(3, 12)     # subrange 3..12, contains 10 items
            subrange(-7, 4)     # subrange -7..4, contains 12 items

        The ``min`` limit must be less than or equal to ``max``.
        Reversed or empty subranges are not allowed. If limits coincide,
        the subrange consists of a single item equal to them. In this
        case ``max`` may be omitted in the parameters list::

            subrange(2, 2)      # subrange 2..2, contains one item
            subrange(8)         # subrange 8..8, contains one item

        This method allows a number of alternative ways of supplying the
        limits. Parameter ``args`` may be assigned with:

        * two integer values ``min, max`` passed as separate positional
            arguments (described above)

        * single integer ``value`` that is considered as the ``min`` and
            ``max`` limit simultaneously (described above)

        * couple of two integer values ``(min, max)`` passed as one
            positional argument. Actually it may be either `tuple` or
            `list` instance

        * dictionary with ``min`` and ``max`` entries

        * another instance of subrange class

        Examples::

            subrange(3, 12)
            subrange(8)
            subrange((3, 12))
            subrange([3, 12])
            subrange({'min': 3, 'max': 12})
            subrange(subrange(3, 12))

        """

        if not args:
            value_error = ValueError("initializer omitted")
            raise value_error

        elif len(args) == 1:
            arg = args[0]

            if isinstance(arg, subrange):
                min_, max_ = arg.min, arg.max

            elif isinstance(arg, dict):
                absent_entries = {'min', 'max'} - set(arg.viewkeys())
                if absent_entries:
                    type_error = TypeError(
                        "initializing dictionary does not define %s"
                        % ', '.join("%r" % key for key in absent_entries))
                    raise type_error
                min_, max_ = arg['min'], arg['max']

            elif isinstance(arg, tuple) or isinstance(arg, list):
                if len(arg) != 2:
                    type_error = TypeError(
                        "initializing %r contains %d item(s), must be 2"
                        % (type(arg).__name__, len(arg)))
                    raise type_error
                min_, max_ = arg

            else:
                min_ = max_ = arg

        elif len(args) == 2:
            min_, max_ = args

        else:
            value_error = ValueError("too many initializers")
            raise value_error

        if type(min_) is not int or type(max_) is not int:
            type_error = TypeError(
                "invalid limits: min=%r, max=%r" % (min_, max_))
            raise type_error

        if min_ > max_:
            value_error = ValueError(
                "reversed limits: min=%d, max=%d" % (min_, max_))
            raise value_error

        self = object.__new__(cls)

        self.min, self.max = min_, max_

        self.__hash = hash((min_, max_) if min_ != max_ else min_)

        self.__repr = "subrange(%r, %r)" % (min_, max_)

        self.__str = subrange.__format__(self, "")

        return self

    def __setattr__(self, name, value):
        """Create new attribute; prohibit modifying existing attribute.

        :arg str name: attribute name
        :arg value: attribute value

        Subrange instances have fully immutable core. It includes
        ``min`` and ``max`` public attributes and some private ones that
        are assigned and frozen during new instance initialization and
        define all the behavior of a particular instance.

        Instances of `subrange` class and its subclasses are allowed to
        have additional custom attributes. All such attributes will
        allow only initial assignment and may be considered as
        additional immutable sublayers::

            self.myattr = 123   # Ok
            self.min = 111      # exception is raised

        """

        if hasattr(self, name):
            attribute_error = AttributeError(
                "attribute %r of %r objects is not writable"
                % (name, self.__class__.__name__))
            raise attribute_error

        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        """Prohibit deletion of existing attribute.

        :arg str name: attribute name

        This function does nothing but raises exception::

            del self.myattr     # exception is raised
            del self.min        # exception is raised

        """

        if hasattr(self, name):
            attribute_error = AttributeError(
                "attribute %r of %r objects is not writable"
                % (name, self.__class__.__name__))
        else:
            attribute_error = AttributeError(
                "%r object has no attribute %r"
                % (self.__class__.__name__, name))

        raise attribute_error

    def __repr__(self):
        """Return formal representation of this subrange.

        :returns: string representing this instance

        Formal representation follows the format string::

            "subrange({min:d}, {max:d})"

        Example::

            repr(subrange(1, 2))    # subrange(1, 2)
            repr(subrange(3))       # subrange(3, 3)

        """

        return self.__repr

    def __str__(self):
        """Return default formatting of this subrange.

        :returns: string with default formatting of this instance

        Default formatting follows one of the format strings::

            "{min:d}..{max:d}"
            "{min:d}"

        The second one is used when ``min == max``, otherwise the first
        format string is used::

            str(subrange(1, 2))    # 1..2
            str(subrange(3))       # 3

        """

        return self.__format__(format_spec="")

    def __format__(self, format_spec):
        """Return formatted representation of this subrange.

        :arg str format_spec: format specification
        :returns: string with custom formatting of this instance

        Custom formatting follows one of the format strings::

            "{min:{format_spec}}"
            "{min:{format_spec}}..{max:{format_spec}}"

        The second one is used when ``min == max``, otherwise the first
        format string is used::

            "0x{:02X}".format(subrange(10, 20))     # 0x0A..14
            "0x{:02X}".format(subrange(10))         # 0x0A

        If ``format_spec`` is empty, the default format specification
        ``{:d}`` is used. See `__str__` also::

            "{}".format(subrange(10, 20))           # 10..20
            "{}".format(subrange(10))               # 10

        """

        if not format_spec and hasattr(self, '_subrange__str'):
            return self.__str

        if self.min == self.max:
            return self.min.__format__(format_spec)

        return "{min:{0}}..{max:{0}}".format(format_spec, **self.__dict__)

    def __hash__(self):
        """Return hash value of this subrange.

        :returns: integer hash value

        Subrange instance's hash completely depends on ``min`` and
        ``max`` attributes. Two instances with the same limits will have
        the same hash. Indeed, such instances are considered equal, see
        `__eq__` method::

            hash(subrange(1, 2)) == hash(subrange(1, 2))    # True
            hash(subrange(1, 2)) == hash(subrange(1, 3))    # False

        Note that single-item subrange's hash equals to the hash of its
        only item. This follows the definition of `__eq__` method that
        considers single-item subrange equal to its only item::

            hash(subrange(3, 3)) == hash(3)     # True
            hash(subrange(3, 3)) == hash(3.0)   # True

        Some more examples::

            r = subrange(3, 12)
            s = subrange(3, 12)
            t = subrange(13, 18)

            d = {r: 111, t: 222}
            e = {r}

            d[r], d[s], d[t]            # 111, 111, 222
            r in e, s in e, t in e      # True, True, False

            p = subrange(2)
            q = subrange(8)

            d = {p: 111, 8: 222}
            e = {p, 8}

            d[p], d[2], d[q], d[8]      # 111, 111, 222, 222
            2 in e, q in e, 9 in e      # True, True, False

        """

        return self.__hash

    def __eq__(self, other):
        """Test if ``self`` is equal to ``other``.

        :arg other: another `subrange` instance, integer value, or a
            different type object
        :returns: `True` if ``self`` is equal to ``other``; `False`
            if they are different

        Two subranges are considered equal if and only if they have the
        same limits, the same ``min`` and the same ``max`` values::

            subrange(1, 2) == subrange(1, 2)    # True
            subrange(1, 2) == subrange(1, 3)    # False

        If ``other`` is not a subrange it still may be compared with the
        ``self``, but only if ``self`` is a single-item subrange. In
        such case that item is compared with ``other`` by value -- i.e.,
        ``self`` is considered a simple integer value::

            subrange(3, 3) == 3         # True
            subrange(3, 3) == 3.0       # True
            3 == subrange(3, 3)         # True

        If ``other`` is not a subrange and ``self`` incorporates more
        than one item then ``self`` and ``other`` are different::

            subrange(3, 4) == 3         # False
            subrange(3, 4) == "3..4"    # False

        """

        if isinstance(other, subrange):
            return self.min == other.min and self.max == other.max

        return self.min == self.max == other

    def __ne__(self, other):
        """Test if ``self`` is not equal to ``other``.

        :arg other: another `subrange` instance, integer value, or a
            different type object
        :returns: `True` if ``self`` is not equal to ``other``; `False`
            if they are the same

        Two items, one or both of which are subranges, considered
        different if and only if they are not equal. See `__eq__` for
        more details.
        """

        return not self == other

    def __lt__(self, other):
        """Test if ``self`` is strictly less than ``other``.

        :arg other: another `subrange` instance, integer value, or a
            different type object
        :returns: `True` if ``self`` is strictly less than ``other``;
            `False` otherwise

        This ``self`` subrange is considered strictly less than the
        ``other`` subrange or value if and only if all items of ``self``
        subrange are less than all items of the ``other`` subrange::

            subrange(1, 2) < subrange(3, 4)     # True
            subrange(1, 2) < 3                  # True
            subrange(1, 2) < 2.5                # True
            3 > subrange(1, 2)                  # True

            subrange(1, 2) < subrange(2, 4)     # False
            subrange(1, 3) < subrange(2, 4)     # False
            subrange(2, 3) < subrange(1, 4)     # False
            subrange(1, 2) < 2                  # False
            2 > subrange(1, 2)                  # False

        .. note::

            Subranges are not subsets with respect to comparison
            operation. Their behavior is more like that of numbers.

        """

        if isinstance(other, subrange):
            return self.max < other.min

        return self.max < other

    def __gt__(self, other):
        """Test if ``self`` is strictly greater than ``other``.

        :arg other: another `subrange` instance, integer value, or a
            different type object
        :returns: `True` if ``self`` is strictly greater than ``other``;
            `False` otherwise

        This ``self`` subrange is considered strictly greater than the
        ``other`` subrange or value if and only if all items of ``self``
        subrange are greater than all items of the ``other`` subrange::

            subrange(3, 4) > subrange(1, 2)     # True
            subrange(1, 2) > 0                  # True
            subrange(1, 2) > 0.5                # True
            0 < subrange(1, 2)                  # True

            subrange(2, 4) > subrange(1, 2)     # False
            subrange(2, 4) > subrange(1, 3)     # False
            subrange(1, 4) > subrange(2, 3)     # False
            subrange(1, 2) > 1                  # False
            1 < subrange(1, 2)                  # False

        .. note::

            Subranges are not subsets with respect to comparison
            operation. Their behavior is more like that of numbers.

        """

        if isinstance(other, subrange):
            return self.min > other.max

        return self.min > other

    def __le__(self, other):
        """Test if ``self`` is less than or equal to ``other``.

        :arg other: another `subrange` instance, integer value, or a
            different type object
        :returns: `True` if ``self`` is less than or equal to ``other``;
            `False` otherwise

        See `__lt__` and `__eq__` for more details.

        .. note::

            The following expressions evaluate to `False`::

                subrange(1, 2) <= 2                 # False
                subrange(1, 2) <= subrange(2, 2)    # False
                subrange(1, 2) <= subrange(2, 3)    # False

            This is so because, according to formal definition, not all
            items of subrange to the left are less than all items of
            subrange to the right, and these subranges are not equal.

        """

        return self < other or self == other

    def __ge__(self, other):
        """Test if ``self`` is greater than or equal to ``other``.

        :arg other: another `subrange` instance, integer value, or a
            different type object
        :returns: `True` if ``self`` is greater than or equal to
            ``other``; `False` otherwise

        See `__gt__` and `__eq__` for more details.

        .. note::

            The following expressions evaluate to `False`::

                subrange(1, 2) >= 1                 # False
                subrange(1, 2) >= subrange(1, 1)    # False
                subrange(1, 2) >= subrange(0, 1)    # False

            This is so because, according to formal definition, not all
            items of subrange to the left are greater than all items of
            subrange to the right, and these subranges are not equal.

        """

        return self > other or self == other

    def __int__(self):
        """Convert subrange to `int` data type.

        :returns: integer value of the only item if ``self`` is a
            single-item subrange; otherwise exception is raised

        Subrange may be converted to integer if and only if it consists
        of a single item. That value is returned here::

            int(subrange(3, 3))     # 3
            int(subrange(1, 2))     # raises exception

        """

        if self.min != self.max:
            value_error = TypeError(
                "subrange contains more than one item "
                "and cannot be converted to 'int'")
            raise value_error

        return self.min

    def __nonzero__(self):
        """Convert subrange to `bool` data type.

        :returns: `True` if ``self`` is not equal to zero value; `False`
            if it equals zero

        Subrange is considered `False` (or equal to zero value) if and
        only if it consists of a single item and its value is zero. This
        follows the definition of `__eq__` and `__int__` methods::

            bool(subrange(0, 0))    # False
            bool(subrange(0, 1))    # True
            bool(subrange(1, 1))    # True

        """

        return self != 0

    def __len__(self):
        """Return the number of items in the subrange.

        :returns: number of items in the subrange

        Subrange is a continuous set of integer numbers between subrange
        limits, including these limits themselves::

            len(subrange(3, 12))    # 10
            len(subrange(-7, 4))    # 12
            len(subrange(2, 2))     # 1
            len(subrange(8))        # 1

        """

        return self.max - self.min + 1

    def __getitem__(self, key):
        """Return ``key``th item in the subrange.

        :arg int key: the requested item's index
        :returns: the ``key``th item in the subrange

        Subranges as ordered collections support random access by
        integer index. Normally index ``key`` must be in the range
        ``0..len-1``. Negative indices are treated as ``len + key``::

            subrange(3, 12)[0]      # 3
            subrange(3, 12)[1]      # 4
            subrange(3, 12)[9]      # 12
            subrange(3, 12)[-1]     # 12
            subrange(3, 12)[-2]     # 11

        Slices are not supported.
        """

        if not isinstance(key, int):
            type_error = TypeError(
                "%s indices must be integers, not %s"
                % (self.__class__.__name__, type(key).__name__))
            raise type_error

        span = self.max - self.min

        if 0 <= key <= span:
            return self.min + key

        if -span <= key + 1 <= 0:
            return self.max + key + 1

        index_error = IndexError(
            "%s index out of range" % self.__class__.__name__)
        raise index_error

    def __iter__(self):
        """Iterate the subrange.

        :returns: iterable yielding the sequence of integer values
            starting with ``min`` and up to ``max`` inclusively

        Example::

            [i for i in subrange(3, 5)]     # [3, 4, 5]
            [i for i in subrange(3)]        # [3]

        """

        for value in xrange(self.min, self.max + 1):
            yield value

    def __reversed__(self):
        """Iterate the subrange in the reversed order.

        :returns: iterable yielding the sequence of integer values
            starting with ``max`` and down to ``min`` inclusively

        Example::

            [i for i in reversed(subrange(3, 5))]   # [5, 4, 3]
            [i for i in reversed(subrange(3))]      # [3]

        """

        for value in xrange(self.max, self.min - 1, -1):
            yield value

    def __contains__(self, item):
        """Test if ``item`` is contained by the subrange.

        :arg item: the tested value
        :returns: `True` if ``item`` is contained by the subrange;
            `False` otherwise

        An ``item`` is contained by (or belongs to) subrange if and only
        if the ``item`` value is between the subrange limits or
        coincides with either of the limits.

        A non-integer ``item`` (`float`, etc.) is considered belonging
        to subrange on same conditions as above even if its value is not
        equal exactly to one of integer values in the subrange::

            3 in subrange(3, 5)         # True
            4 in subrange(3, 5)         # True
            6 in subrange(3, 5)         # False
            3.75 in subrange(3, 5)      # True
            5.0 in subrange(3, 5)       # True

        """

        return self.min <= item <= self.max


class subrangef(subrange):
    """Annotated `subrange` with reach formatting capabilities.

    This class inherits all the behavior of its superclass `subrange`.
    Additionally it accepts custom attributes, annotations, that may be
    referenced further in default and custom formatting.

    See documentation on methods for more details.
    """

    def __new__(cls, *args, **kwargs):
        """Create and initialize a new instance of `subrangef`.

        :arg tuple args: couple of integers or a complex initializer
        :arg dict kwargs: optional custom attributes and ``str_spec``
            that defines the default string format specification
        :returns: newly created and initialized instance of `subrangef`

        See `subrange.__new__` for details on how ``min`` and ``max``
        parameters are passed with ``args`` and then processed.

        Optional ``kwargs`` dictionary delivers custom attributes,
        annotations, if application needs them. All of them are included
        into the dictionary of public attributes of the newly created
        instance and may be referenced further.

        This class also features reach formatting based on `format`
        built-in function and `__format__` method. New instance may be
        assigned with custom format string using ``str_spec`` parameter
        that is passed with ``kwargs``. It will define the default
        formatting of this instance.

        The format string ``str_spec`` may reference core attributes::

            # by default {value} field is used which resolves either to
            # 'min' or 'min..max' format depending on whether this
            # subrange is or is not a single-item subrange
            a = subrangef(10)
            print a     # 10

            # it may be changed to force 'min..max' format
            b = subrangef(10, str_spec="{min}..{max}")
            print b     # 10..10

        It may specify different ``format_spec``::

            # by default {:d} format specification is used
            c = subrangef(10, 20)
            print c     # 10..20

            # it may be changed, for example, to hexadecimal format
            d = subrangef(10, 20, str_spec="0x{value:04X}")
            print d     # 0x000A..0014

        It may reference custom annotation attributes. If necessary,
        ``conversion`` may be specified::

            e = subrangef(10, 20, str_spec="{value} {brief!r}",
                          brief="my subrange")
            print e     # 10..20 'my subrange'

        And it may use literal text::

            f = subrangef(10, 20,
                          str_spec="0b{value:06b} <{id}> -- {comm}",
                          id="VALID_RNG",
                          comm="valid range")
            print f     # 0b001010..010100 <VALID_RNG> -- valid range

        The default format string may be replaced with a custom one::

            print "0x{:04X}".format(f)
            # 0x000A..0014

            print "{id}: 0x{value:04X}".format(**f.__dict__)
            # VALID_RNG: 0x000A..0014

            print "{id} = {value!r}".format(**f.__dict__)
            # VALID_RNG = subrange(10, 20)

            print "min of {comm} is {value.min}".format(**f.__dict__)
            print "min of {comm} is {min}".format(**f.__dict__)
            # min of valid range is 10

        """

        self = subrange.__new__(cls, *args)

        kwargs.update(self.__dict__)
        self.__dict__.update(kwargs)

        self.value = subrange(*args)

        self.__str = str(kwargs.get("str_spec", "{value}")
                         ).format(**self.__dict__)

        return self

    def __format__(self, format_spec):
        """Return formatted representation of this subrange.

        :arg str format_spec: format specification
        :returns: string with custom formatting of this instance

        Custom formatting follows one of the format strings::

            "{min:{format_spec}}"
            "{min:{format_spec}}..{max:{format_spec}}"

        The second one is used when ``min == max``, otherwise the first
        format string is used::

            "0x{:02X}".format(subrangef(10, 20))    # 0x0A..14
            "0x{:02X}".format(subrangef(10))        # 0x0A

        If ``format_spec`` is empty, the default format specification
        is used that was initially assigned with ``str_spec`` parameter
        of the `__new__` method. See `__str__` also::

            r = subrangef(10, 20, str_spec="0x{value:04X}")
            s = subrangef(10, 10, str_spec="0x{value:04X}")
            "{}".format(r)      # 0x000A..0014
            "{}".format(s)      # 0x000A

        """

        if not format_spec:
            return self.__str

        return self.value.__format__(format_spec)
