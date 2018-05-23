# Copyright 2018 Robert Haas
# For license information, see LICENSE.TXT in the package root directory

from multiprocessing import cpu_count as _cpu_count

_DETECTED_NUM_CORES = _cpu_count()


def dask(function, argument_list, num_cores=None):
    """Apply a univariate function to a list of arguments in a parallel fashion.

    Uses Dask's delayed() function to build a task graph and compute() function to
    calculate results.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments
        num_cores (optional): Number of cores to use for calculation.

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> dask(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
        - https://dask.pydata.org
        - https://dask.pydata.org/en/latest/scheduler-overview.html
        - https://dask.pydata.org/en/latest/delayed.html
    """
    from dask import compute, delayed
    from dask import multiprocessing as _multiprocessing

    if num_cores is None:
        num_cores = _DETECTED_NUM_CORES

    jobs_generator = (delayed(function)(arg) for arg in argument_list)
    result_tuple = compute(*jobs_generator, get=_multiprocessing.get, num_workers=num_cores)
    result_list = list(result_tuple)
    return result_list


def futures(function, argument_list, num_cores=None):
    """Apply a univariate function to a list of arguments in a parallel fashion.

    Uses Python's built-in futures with a process pool executor.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments
        num_cores (optional): Number of cores to use for calculation.

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> futures(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
     - https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Executor.map
    """
    # TODO: possible bug that leads to freezing, see
    # https://stackoverflow.com/questions/48218897/python-doctest-hangs-using-processpoolexecutor

    from concurrent.futures import ProcessPoolExecutor

    if num_cores is None:
        num_cores = _DETECTED_NUM_CORES

    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        iterator = executor.map(function, argument_list)
        result_list = list(iterator)
        return result_list


def joblib(function, argument_list, num_cores=None):
    """Apply a univariate function to a list of arguments in a parallel fashion.

    Uses Joblib's delayed() function with a parallel executor that starts multiple
    processes.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments
        num_cores (optional): Number of cores to use for calculation.

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> joblib(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
        - https://pythonhosted.org/joblib/parallel.html
    """
    from joblib import delayed, Parallel

    if num_cores is None:
        num_cores = _DETECTED_NUM_CORES

    parallel_executor = Parallel(n_jobs=num_cores, backend='multiprocessing')
    jobs_generator = (delayed(function)(arg) for arg in argument_list)
    result_list = parallel_executor(jobs_generator)
    return result_list


def multiprocessing(function, argument_list, num_cores=None):
    """Apply a univariate function to a list of arguments in a parallel fashion.

    Uses the parallel map() function with a pool of processes from multiprocessing in
    Python's standard library.

    Args:
        function: A callable object that accepts one argument
        argument_list: An iterable object of input arguments
        num_cores (optional): Number of cores to use for calculation.

    Returns:
        List of output results

    Example:
        >>> def square(x):
        ...     return x**2
        ...
        >>> multiprocessing(square, [1, 2, 3, 4, 5])
        [1, 4, 9, 16, 25]

    References:
        - https://docs.python.org/3/library/multiprocessing.html
        - https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.map
    """
    from multiprocessing import Pool

    if num_cores is None:
        num_cores = _DETECTED_NUM_CORES

    pool = Pool(processes=num_cores)
    result_list = pool.map(function, argument_list)
    return result_list
