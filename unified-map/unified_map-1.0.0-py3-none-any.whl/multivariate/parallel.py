# Copyright 2018 Robert Haas
# For license information, see LICENSE.TXT in the package root directory

from multiprocessing import cpu_count as _cpu_count

_DETECTED_NUM_CORES = _cpu_count()


def dask(function, argument_list, num_cores=None):
    """Apply a multivariate function to a list of arguments in a parallel fashion.

    Uses Dask's delayed() function to build a task graph and compute() function to
    calculate results.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections
        num_cores (optional): Number of cores to use for calculation.

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> dask(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://dask.pydata.org
        - https://dask.pydata.org/en/latest/scheduler-overview.html
        - https://dask.pydata.org/en/latest/delayed.html
    """
    from dask import compute, delayed
    from dask import multiprocessing as _multiprocessing

    if num_cores is None:
        num_cores = _DETECTED_NUM_CORES

    jobs_generator = (delayed(function)(*args) for args in argument_list)
    result_tuple = compute(*jobs_generator, get=_multiprocessing.get, num_workers=num_cores)
    result_list = list(result_tuple)
    return result_list


def futures(function, argument_list, num_cores=None):
    """Apply a multivariate function to a list of arguments in a parallel fashion.

    Uses Python's built-in futures with a process pool executor.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections
        num_cores (optional): Number of cores to use for calculation.

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> futures(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Executor.map
    """
    # TODO: possible bug that leads to freezing, see
    # https://stackoverflow.com/questions/48218897/python-doctest-hangs-using-processpoolexecutor

    from concurrent.futures import ProcessPoolExecutor

    if num_cores is None:
        num_cores = _DETECTED_NUM_CORES

    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        iterator = executor.map(function, *zip(*argument_list))
        result_list = list(iterator)
        return result_list


def joblib(function, argument_list, num_cores=None):
    """Apply a multivariate function to a list of arguments in a parallel fashion.

    Uses Joblib's delayed() function with a parallel executor that starts multiple
    processes.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections
        num_cores (optional): Number of cores to use for calculation.

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> joblib(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://pythonhosted.org/joblib/parallel.html
    """
    # TODO: fix doctest problem arising from having stuff in the closure that cannot be pickled
    # http://apache-spark-developers-list.1001551.n3.nabble.com/Problems-with-Pyspark-Dill-tests-td7052.html

    from joblib import delayed, Parallel

    if num_cores is None:
        num_cores = _DETECTED_NUM_CORES

    parallel_executor = Parallel(n_jobs=num_cores, backend='multiprocessing')
    jobs_generator = (delayed(function)(*args) for args in argument_list)
    result_list = parallel_executor(jobs_generator)
    return list(result_list)


def multiprocessing(function, argument_list, num_cores=None):
    """Apply a multivariate function to a list of arguments in a parallel fashion.

    Uses the parallel map() function with a pool of processes from multiprocessing in
    Python's standard library.

    Args:
        function: A callable object that accepts more than one argument
        argument_list: An iterable object of input argument collections
        num_cores (optional): Number of cores to use for calculation.

    Returns:
        List of output results

    Example:
        >>> def add(x, y, z):
        ...     return x+y+z
        ...
        >>> multiprocessing(add, [(1, 2, 3), (10, 20, 30)])
        [6, 60]

    References:
        - https://docs.python.org/3/library/multiprocessing.html
        - https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.starmap
    """
    from multiprocessing import Pool

    if num_cores is None:
        num_cores = _DETECTED_NUM_CORES

    pool = Pool(processes=num_cores)
    result_list = pool.starmap(function, argument_list)
    return result_list
