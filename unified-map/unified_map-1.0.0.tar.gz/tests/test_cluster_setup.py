import socket

import pytest

import unified_map as umap


# Addresses

def test_address_verification():
    correct_examples = [
        '127.0.0.1:7077',
        'spark://127.0.0.1:7077',
        'tcp://127.0.0.1:7077',
    ]

    incorrect_examples = [
        'nonsense',
        'utter:nonsense',
        'is://just:wrong',
        '127.0.0.1',
        ':7077',
        '7077',
        '://127.0.0.1:42',
        'tcp://127.0.0.1',
    ]

    for address in correct_examples:
        umap.cluster_setup._verify_address(address)

    for address in incorrect_examples:
        with pytest.raises(ValueError):
            umap.cluster_setup._verify_address(address)


def test_address_parsing():
    input_output_expectations = [
        ['127.0.0.1:7077', (None, '127.0.0.1', '7077')],
        ['tcp://127.0.0.1:7077', ('tcp', '127.0.0.1', '7077')],
        ['spark://127.0.0.1:7077', ('spark', '127.0.0.1', '7077')],
    ]
    for address, expected_result in input_output_expectations:
        result = umap.cluster_setup._parse_address(address)
        assert result == expected_result


# Dask

def test_dask_report():
    umap.cluster_setup.dask._connection = None
    umap.cluster_setup.dask.report_status()


def test_dask_scheduler_fail_on_unavailable_address():
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Use an address
        try:
            skt.bind(('127.0.0.1', 8789))
        except Exception:
            pass

        # Fail when trying to use same address
        with pytest.raises(ConnectionError):
            umap.cluster_setup.dask.start_scheduler('127.0.0.1:8789')
    finally:
        skt.close()


@pytest.mark.skip(reason='Currently hangs, worker does not know there is no scheduler')
def test_dask_start_worker_fail_on_inexistent_scheduler():
    with pytest.raises(ConnectionError):
        umap.cluster_setup.dask.start_worker('127.0.0.1:1111111111')


def test_dask_connect_to_scheduler_fail_on_inexistent_scheduler():
    with pytest.raises(ConnectionError):
        umap.cluster_setup.dask.connect_to_scheduler('127.0.0.1:1111111111')


# Spark

def test_spark_report():
    umap.cluster_setup.spark._connection = None
    umap.cluster_setup.spark.report_status()


def test_spark_scheduler_fail_on_unavailable_address():
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Use an address
        try:
            skt.bind(('127.0.0.1', 7077))
        except Exception:
            pass

        # Fail when trying to use same address
        with pytest.raises(ConnectionError):
            umap.cluster_setup.spark.start_scheduler('127.0.0.1:7077')
    finally:
        skt.close()


@pytest.mark.skip(reason='Currently hangs, worker does not know there is no scheduler')
def test_spark_start_worker_fail_on_inexistent_scheduler():
    with pytest.raises(ConnectionError):
        umap.cluster_setup.spark.start_worker('127.0.0.1:1111111111')


def test_spark_connect_to_scheduler_fail_on_inexistent_scheduler():
    with pytest.raises(ConnectionError):
        umap.cluster_setup.spark.connect_to_scheduler('127.0.0.1:1111111111')
