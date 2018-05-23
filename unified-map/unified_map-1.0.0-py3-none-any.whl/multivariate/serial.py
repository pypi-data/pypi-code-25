# Copyright 2018 Robert Haas
# For license information, see LICENSE.TXT in the package root directory

_map_alias = map


def for_loop(function, argument_list):
    """Apply a multivariate function to a list of arguments in a serial fashion.

    Uses Python's built-in for statement.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> for_loop(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://docs.python.org/3/reference/compound_stmts.html#the-for-statement
        - https://docs.python.org/3/tutorial/controlflow.html#for-statements
    """
    result_list = []
    for args in argument_list:
        result_list.append(function(*args))
    return result_list


def generator_expression(function, argument_list):
    """Apply a multivariate function to a list of arguments in a serial fashion.

    Uses Python's built-in generator expressions.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> generator_expression(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://www.python.org/dev/peps/pep-0289
    """
    gen_expr = (function(*args) for args in argument_list)
    result_list = list(gen_expr)
    return result_list


def generator_function(function, argument_list):
    """Apply a multivariate function to a list of arguments in a serial fashion.

    Uses Python's built-in generator function syntax to return a generator iterator.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> generator_function(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://docs.python.org/3/reference/simple_stmts.html#the-yield-statement
        - https://docs.python.org/3/glossary.html#term-generator
    """
    def generator_func(function, argument_list):
        for args in argument_list:
            yield function(*args)

    generator_iterator = generator_func(function, argument_list)
    result_list = list(generator_iterator)
    return result_list


def list_comprehension(function, argument_list):
    """Apply a multivariate function to a list of arguments in a serial fashion.

    Uses Python's built-in list comprehension.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> list_comprehension(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    """
    result_list = [function(*args) for args in argument_list]
    return result_list


def map(function, argument_list):
    """Apply a multivariate function to a list of arguments in a serial fashion.

    Uses Python's built-in map() and zip() functions.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> map(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://docs.python.org/3/library/functions.html#map
    """
    iterator = _map_alias(function, *zip(*argument_list))
    result_list = list(iterator)
    return result_list


def starmap(function, argument_list):
    """Apply a multivariate function to a list of arguments in a serial fashion.

    Uses the starmap() function from itertools in Python's standard library.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> starmap(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://docs.python.org/3/library/itertools.html#itertools.starmap
    """
    from itertools import starmap as _starmap

    iterator = _starmap(function, argument_list)
    result_list = list(iterator)
    return result_list
