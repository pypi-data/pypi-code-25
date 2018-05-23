import pytest

import unified_map as ue


# Common preliminaries

def f_fast(x):
    return x**2


def slow_computation():
    num = 1.0
    for i in range(1000000):
        num = num / 42.0 * 42.0
    return num


def f_slow(x):
    slow_computation()
    return f_fast(x)


n_args = 20
args = [x for x in range(n_args)]
expected_results = [f_fast(arg) for arg in args]


# Tests with pytest and pytest-benchmark (https://pypi.python.org/pypi/pytest-benchmark)

# Serial

def test_serial_for_loop(benchmark):
    results = benchmark(ue.univariate.serial.for_loop, f_slow, args)
    assert results == expected_results


def test_serial_generator_expression(benchmark):
    results = benchmark(ue.univariate.serial.generator_expression, f_slow, args)
    assert results == expected_results


def test_serial_generator_function(benchmark):
    results = benchmark(ue.univariate.serial.generator_function, f_slow, args)
    assert results == expected_results


def test_serial_list_comprehension(benchmark):
    results = benchmark(ue.univariate.serial.list_comprehension, f_slow, args)
    assert results == expected_results


def test_serial_map(benchmark):
    results = benchmark(ue.univariate.serial.map, f_slow, args)
    assert results == expected_results


def test_serial_starmap(benchmark):
    results = benchmark(ue.univariate.serial.starmap, f_slow, args)
    assert results == expected_results


# Parallel

def test_parallel_dask(benchmark):
    results = benchmark(ue.univariate.parallel.dask, f_slow, args)
    assert results == expected_results


def test_parallel_joblib(benchmark):
    results = benchmark(ue.univariate.parallel.joblib, f_slow, args)
    assert results == expected_results


def test_parallel_futures(benchmark):
    results = benchmark(ue.univariate.parallel.futures, f_slow, args)
    assert results == expected_results


def test_parallel_multiprocessing(benchmark):
    results = benchmark(ue.univariate.parallel.multiprocessing, f_slow, args)
    assert results == expected_results


# Distributed

# Cannot be tested in a general way since it includes starting workers on a cluster
