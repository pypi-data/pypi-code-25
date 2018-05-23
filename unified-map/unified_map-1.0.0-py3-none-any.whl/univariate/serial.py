# Copyright 2018 Robert Haas
# For license information, see LICENSE.TXT in the package root directory

_map_alias = map


def for_loop(function, argument_list):
    """Apply a univariate function to a list of arguments in a serial fashion.

    Uses Python's built-in for statement.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> for_loop(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
        - https://docs.python.org/3/reference/compound_stmts.html#the-for-statement
        - https://docs.python.org/3/tutorial/controlflow.html#for-statements
    """
    result_list = []
    for arg in argument_list:
        result_list.append(function(arg))
    return result_list


def generator_expression(function, argument_list):
    """Apply a univariate function to a list of arguments in a serial fashion.

    Uses Python's built-in generator expressions.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> generator_expression(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
        - https://www.python.org/dev/peps/pep-0289
    """
    gen_expr = (function(arg) for arg in argument_list)
    result_list = list(gen_expr)
    return result_list


def generator_function(function, argument_list):
    """Apply a univariate function to a list of arguments in a serial fashion.

    Uses Python's built-in generator function syntax to return a generator iterator.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> generator_function(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
        - https://docs.python.org/3/reference/simple_stmts.html#the-yield-statement
        - https://docs.python.org/3/glossary.html#term-generator
    """
    def generator_func(function, argument_list):
        for arg in argument_list:
            yield function(arg)

    generator_iterator = generator_func(function, argument_list)
    result_list = list(generator_iterator)
    return result_list


def list_comprehension(function, argument_list):
    """Apply a univariate function to a list of arguments in a serial fashion.

    Uses Python's built-in list comprehension.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> list_comprehension(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
        - https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    """
    result_list = [function(arg) for arg in argument_list]
    return result_list


def map(function, argument_list):
    """Apply a univariate function to a list of arguments in a serial fashion.

    Uses Python's built-in map() function.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> map(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
        - https://docs.python.org/3/library/functions.html#map
    """
    iterator = _map_alias(function, argument_list)
    result_list = list(iterator)
    return result_list


def starmap(function, argument_list):
    """Apply a univariate function to a list of arguments in a serial fashion.

    Uses the starmap() function from itertools in Python's standard library and
    Python's built-in zip() function.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> starmap(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
        - https://docs.python.org/3/library/itertools.html#itertools.starmap
    """
    from itertools import starmap as _starmap

    iterator = _starmap(function, zip(argument_list))
    result_list = list(iterator)
    return result_list
