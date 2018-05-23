import pytest

import unified_map as ue


# Common preliminaries

def f_fast(x, y, z):
    return x**2 + y**2 + z**2


def slow_computation():
    num = 1.0
    for i in range(1000000):
        num = num / 42.0 * 42.0
    return num


def f_slow(x, y, z):
    slow_computation()
    return f_fast(x, y, z)


n_args = 20
args = [(x, x+1, x+2) for x in range(n_args)]
expected_results = [f_fast(*arg) for arg in args]


# Tests with pytest and pytest-benchmark (https://pypi.python.org/pypi/pytest-benchmark)

# Serial

def test_serial_for_loop(benchmark):
    results = benchmark(ue.multivariate.serial.for_loop, f_slow, args)
    assert results == expected_results


def test_serial_generator_expression(benchmark):
    results = benchmark(ue.multivariate.serial.generator_expression, f_slow, args)
    assert results == expected_results


def test_serial_generator_function(benchmark):
    results = benchmark(ue.multivariate.serial.generator_function, f_slow, args)
    assert results == expected_results


def test_serial_list_comprehension(benchmark):
    results = benchmark(ue.multivariate.serial.list_comprehension, f_slow, args)
    assert results == expected_results


def test_serial_map(benchmark):
    results = benchmark(ue.multivariate.serial.map, f_slow, args)
    assert results == expected_results


def test_serial_starmap(benchmark):
    results = benchmark(ue.multivariate.serial.starmap, f_slow, args)
    assert results == expected_results


# Parallel

def test_parallel_dask(benchmark):
    results = benchmark(ue.multivariate.parallel.dask, f_slow, args)
    assert results == expected_results


def test_parallel_joblib(benchmark):
    results = benchmark(ue.multivariate.parallel.joblib, f_slow, args)
    assert results == expected_results


def test_parallel_futures(benchmark):
    results = benchmark(ue.multivariate.parallel.futures, f_slow, args)
    assert results == expected_results


def test_parallel_multiprocessing(benchmark):
    results = benchmark(ue.multivariate.parallel.multiprocessing, f_slow, args)
    assert results == expected_results


# Distributed

# Cannot be tested in a general way since it includes starting workers on a cluster
