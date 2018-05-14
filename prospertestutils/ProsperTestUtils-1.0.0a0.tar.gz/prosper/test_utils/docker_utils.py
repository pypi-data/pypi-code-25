"""common test utilities for Prosper projects"""
import docker
import pytest

from . import exceptions

DOCKER_OK = None
def assert_docker(xfail=False, force_retry=False, **kwargs):
    """validates docker connection

    Args:
        xfail (bool): change behavior from rasie->xfail
        force_retry (bool): force recheck docker status
        kwargs: docker.from_env() handles

    Raises
        pytest.xfail: soft-fail for expected failure
        exceptions.DockerNotFound: no docker connection

    """
    global DOCKER_OK
    if DOCKER_OK == None or force_retry:
        try:
            client = docker.from_env(**kwargs)
            client.info()
            DOCKER_OK = True
        except Exception as err:
            DOCKER_OK = False

    if DOCKER_OK:
        return

    if xfail:
        raise pytest.xfail('Docker Not available:')
    else:
        raise exceptions.DockerNotFound()
