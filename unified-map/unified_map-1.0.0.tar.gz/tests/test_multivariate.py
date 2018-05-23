import multiprocessing
import time

import pytest

import unified_map as umap


# Common preliminaries

def f_num(x, y, z):
    return x**2 + y**2 + z**2

args_numerical = [(x, x+1, x+2) for x in list(range(10))]
expected_results_numerical = [f_num(*args) for args in args_numerical]


def f_str(s1, s2):
    return s1+s2+'_suffix'

args_str = [(s, s.upper()) for s in list('abcdefghijklm')]
expected_results_str = [f_str(*args) for args in args_str]


testdata = [
    (f_num, args_numerical, expected_results_numerical),
    (f_str, args_str, expected_results_str)
]


def get_unused_port(address, start_port=8990):
    port = start_port
    while True:
        scheduler_address = '{}:{}'.format(address, port)
        if not umap.cluster_setup._is_address_in_use(scheduler_address):
            print('Using scheduler address', scheduler_address)
            break
        port += 1
    return scheduler_address


def run_func_in_background_process(func, *args):
    proc = multiprocessing.Process(target=func, args=args)
    proc.daemon = True
    proc.start()
    return proc


# Tests with pytest

# Serial

@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_serial_for_loop(f, args, expected_results):
    results = umap.multivariate.serial.for_loop(f, args)
    assert results == expected_results


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_serial_generator_expression(f, args, expected_results):
    results = umap.multivariate.serial.generator_expression(f, args)
    assert results == expected_results


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_serial_generator_function(f, args, expected_results):
    results = umap.multivariate.serial.generator_function(f, args)
    assert results == expected_results


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_serial_list_comprehension(f, args, expected_results):
    results = umap.multivariate.serial.list_comprehension(f, args)
    assert results == expected_results


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_serial_map(f, args, expected_results):
    results = umap.multivariate.serial.map(f, args)
    assert results == expected_results


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_serial_starmap(f, args, expected_results):
    results = umap.multivariate.serial.starmap(f, args)
    assert results == expected_results


# Parallel

@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_parallel_dask(f, args, expected_results):
    results = umap.multivariate.parallel.dask(f, args)
    assert results == expected_results


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_parallel_joblib(f, args, expected_results):
    results = umap.multivariate.parallel.joblib(f, args)
    assert results == expected_results


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_parallel_futures(f, args, expected_results):
    results = umap.multivariate.parallel.futures(f, args)
    assert results == expected_results


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_parallel_multiprocessing(f, args, expected_results):
    results = umap.multivariate.parallel.multiprocessing(f, args)
    assert results == expected_results


# Distributed - tested by spawning scheduler and workers only locally on this machine

@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_distributed_dask_fail(f, args, expected_results):
    # No connection to scheduler (problem: dependency on other tests -> set to None explicitely)
    umap.cluster_setup.dask._connection = None
    with pytest.raises(ConnectionError):
        umap.multivariate.distributed.dask(f, args)


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_distributed_dask(f, args, expected_results):

    def dask_cluster_setup():
        scheduler_address = get_unused_port('127.0.0.1', start_port=8789)
        processes = []
        proc = run_func_in_background_process(
            umap.cluster_setup.dask.start_scheduler, scheduler_address)
        processes.append(proc)
        time.sleep(0.3)
        for _ in range(4):
            proc = run_func_in_background_process(
                umap.cluster_setup.dask.start_worker, scheduler_address)
            processes.append(proc)
        umap.cluster_setup.dask.connect_to_scheduler(scheduler_address)
        return processes

    # Info about scheduler
    umap.cluster_setup.dask.report_status()

    # Distributed evaluation of a function
    processes = dask_cluster_setup()
    results = umap.multivariate.distributed.dask(f, args)
    assert results == expected_results

    for proc in processes:
        proc.terminate()  # "exit handlers and finally clauses, etc., will not be executed."


@pytest.mark.parametrize('f, args, expected_results', testdata)
def test_distributed_spark_fail(f, args, expected_results):
    # No connection to scheduler (problem: dependency on other tests -> set to None explicitely)
    umap.cluster_setup.spark._connection = None
    with pytest.raises(ConnectionError):
        umap.multivariate.distributed.spark(f, args)


def test_distributed_spark():
    # TODO: find out why spark does not work with testdata and function defined elsewhere

    def spark_cluster_setup():
        scheduler_address = get_unused_port('127.0.0.1', start_port=7077)
        processes = []
        proc = run_func_in_background_process(
            umap.cluster_setup.spark.start_scheduler, scheduler_address)
        processes.append(proc)
        time.sleep(2.5)
        proc = run_func_in_background_process(
            umap.cluster_setup.spark.start_worker, scheduler_address)
        processes.append(proc)
        umap.cluster_setup.spark.connect_to_scheduler(scheduler_address)
        return processes

    # Info about scheduler
    umap.cluster_setup.spark.report_status()

    # Distributed evaluation of a function
    processes = spark_cluster_setup()

    def f(x, y):
        return x**2 + y**2
    args = [(x, x+1) for x in range(20)]
    expected_results = [f(*arg) for arg in args]

    results = umap.multivariate.distributed.spark(f, args)
    assert results == expected_results

    for proc in processes:
        proc.terminate()  # "exit handlers and finally clauses, etc., will not be executed."
