# -*- coding: utf-8 -*-

"""Functions for deploying resources to Artifactory."""

import logging
import os
from artifactory import ArtifactoryPath

from .hashing import get_bel_resource_hash
from .today import get_annotation_today, get_knowledge_today, get_namespace_today
from .utils import get_arty_annotation_module, get_arty_knowledge_module, get_arty_namespace_module

__all__ = [
    'deploy_namespace',
    'deploy_annotation',
    'deploy_knowledge',
    'deploy_directory',
]

log = logging.getLogger(__name__)

BELANNO_EXTENSION = '.belanno'
BELNS_EXTENSION = '.belns'
BEL_EXTENSION = '.bel'


def get_arty_auth():
    """Get an authentication 2-tuple for Artifactory.

    Necessitatest the use of the environment variables ``ARTY_USERNAME`` and ``ARTY_PASSWORD``.

    :rtype: tuple[str]
    """
    return os.environ['ARTY_USERNAME'], os.environ['ARTY_PASSWORD']


def _deploy_helper(filename, module_name, get_module, get_today_fn, hash_check=True, auth=None):
    """Deploys a file to the Artifactory BEL namespace cache

    :param str filename: The physical path
    :param str module_name: The name of the module to deploy to
    :param tuple[str] auth: A pair of (str username, str password) to give to the auth keyword of the constructor of
                            :class:`artifactory.ArtifactoryPath`. Defaults to the result of :func:`get_arty_auth`.
    :return: The resource path, if it was deployed successfully, else none.
    :rtype: Optional[str]
    """
    path = ArtifactoryPath(
        get_module(module_name),
        auth=get_arty_auth() if auth is None else auth
    )
    path.mkdir(exist_ok=True)

    if hash_check:
        deployed_semantic_hashes = {
            get_bel_resource_hash(subpath.as_posix())
            for subpath in path
        }

        semantic_hash = get_bel_resource_hash(filename)

        if semantic_hash in deployed_semantic_hashes:
            return  # Don't deploy if it's already uploaded

    target = path / get_today_fn(module_name)
    target.deploy_file(filename)

    log.info('deployed %s', module_name)

    return target.as_posix()


def deploy_namespace(filename, module_name, hash_check=True, auth=None):
    """Deploy a file to the Artifactory BEL namespace cache.

    :param str filename: The physical path
    :param str module_name: The name of the module to deploy to
    :param bool hash_check: Ensure the hash is unique before deploying
    :param tuple[str] auth: A pair of (str username, str password) to give to the auth keyword of the constructor of
                            :class:`artifactory.ArtifactoryPath`. Defaults to the result of :func:`get_arty_auth`.
    :return: The resource path, if it was deployed successfully, else none.
    :rtype: Optional[str]
    """
    return _deploy_helper(
        filename,
        module_name,
        get_arty_namespace_module,
        get_namespace_today,
        hash_check=hash_check,
        auth=auth
    )


def deploy_annotation(filename, module_name, hash_check=True, auth=None):
    """Deploy a file to the Artifactory BEL annotation cache.

    :param str filename: The physical file path
    :param str module_name: The name of the module to deploy to
    :param bool hash_check: Ensure the hash is unique before deploying
    :param tuple[str] auth: A pair of (str username, str password) to give to the auth keyword of the constructor of
                            :class:`artifactory.ArtifactoryPath`. Defaults to the result of :func:`get_arty_auth`.
    :return: The resource path, if it was deployed successfully, else none.
    :rtype: Optional[str]
    """
    return _deploy_helper(
        filename,
        module_name,
        get_arty_annotation_module,
        get_annotation_today,
        hash_check=hash_check,
        auth=auth
    )


def deploy_knowledge(filename, module_name, auth=None):
    """Deploy a file to the Artifactory BEL knowledge cache.

    :param str filename: The physical file path
    :param str module_name: The name of the module to deploy to
    :param tuple[str] auth: A pair of (str username, str password) to give to the auth keyword of the constructor of
                            :class:`artifactory.ArtifactoryPath`. Defaults to the result of :func:`get_arty_auth`.
    :return: The resource path, if it was deployed successfully, else none.
    :rtype: Optional[str]
    """
    return _deploy_helper(
        filename,
        module_name,
        get_arty_knowledge_module,
        get_knowledge_today,
        hash_check=False,
        auth=auth
    )


def deploy_directory(directory, auth=None):
    """Deploy all files in a given directory.

    :param str directory: the path to a directory
    :param tuple[str] auth: A pair of (str username, str password) to give to the auth keyword of the constructor of
                            :class:`artifactory.ArtifactoryPath`. Defaults to the result of :func:`get_arty_auth`.
    """
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)

        if file.endswith(BELANNO_EXTENSION):
            name = file[:-len(BELANNO_EXTENSION)]
            log.info('deploying annotation %s', full_path)
            deploy_annotation(full_path, name, auth=auth)

        elif file.endswith(BELNS_EXTENSION):
            name = file[:-len(BELNS_EXTENSION)]
            log.info('deploying namespace %s', full_path)
            deploy_namespace(full_path, name, auth=auth)

        elif file.endswith(BEL_EXTENSION):
            name = file[:-len(BEL_EXTENSION)]
            log.info('deploying knowledge %s', full_path)
            deploy_knowledge(full_path, name, auth=auth)

        else:
            log.debug('not deploying %s', full_path)
