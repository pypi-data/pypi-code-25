# Copyright 2018 Robert Haas
# For license information, see LICENSE.TXT in the package root directory

from .. import cluster_setup as _cluster_setup


def dask(function, argument_list):
    """Apply a multivariate function to a list of arguments in a distributed fashion.

    Uses Dask's delayed() function to build a task graph and compute() function with
    a cluster connection to calculate results.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections

    Returns:
        List of output results

    Raises:
        ConnectionError: If no connection ("context") to a Spark scheduler ("master")
            was established.

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> dask(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    .. note::
       Requires that a connection to a scheduler has been established,
       see :ref:`cluster-setup` and :ref:`dask-cluster-setup`.

    References:
        - https://dask.pydata.org
        - https://dask.pydata.org/en/latest/delayed.html
    """
    from dask import delayed, compute

    if _cluster_setup.dask._connection is None:
        error_message = (
            'No connection was established to a Dask scheduler that distributes jobs to workers. '
            "Please use unified_map.cluster_setup.dask and/or Dask's command line "
            'interface for\n'
            '  1. Starting a scheduler\n'
            '  2. Starting several workers\n'
            '  3. Connecting to the scheduler')
        raise ConnectionError(error_message)

    jobs = [delayed(function)(*args) for args in argument_list]
    result_tuple = compute(*jobs, get=_cluster_setup.dask._connection.get)
    result_list = list(result_tuple)
    return result_list


def spark(function, argument_list):
    """Apply a multivariate function to a list of arguments in a distributed fashion.

    Uses Apache Spark's map() and collect() functions provided by a
    resilient distributed dataset (RDD).

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections

    Returns:
        List of output results

    Raises:
        ConnectionError: If no connection ("context") to a Spark scheduler ("master")
            was established.

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> spark(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    .. note::
       Requires that a connection to a scheduler has been established,
       see :ref:`cluster-setup` and :ref:`spark-cluster-setup`.

    References:
        - https://spark.apache.org/docs/latest/api/python/index.html
        - https://spark.apache.org/docs/latest/rdd-programming-guide.html
    """
    if _cluster_setup.spark._connection is None:
        error_message = (
            'No connection ("context") was established to a Spark scheduler ("master") that '
            'distributes jobs to workers ("slaves"). '
            "Please use unified_map.cluster_setup.spark and/or Apache Spark's command line "
            'interface for\n'
            '  1. Starting a scheduler\n'
            '  2. Starting several workers\n'
            '  3. Connecting to the scheduler')
        raise ConnectionError(error_message)

    input_rdd = _cluster_setup.spark._connection.parallelize(argument_list)

    def new_function(arg):
        return function(*arg)  # pragma: no cover
    output_rdd = input_rdd.map(new_function)
    results = output_rdd.collect()
    return results
