"""Provides the wrapper class for Argus API"""
import site
import ssl
from distutils.sysconfig import get_python_lib
from os import getenv, makedirs
from os.path import exists, expanduser, join

from datetime import datetime
from requests.exceptions import SSLError, Timeout, ProxyError
from types import ModuleType
from urllib3.exceptions import MaxRetryError

from api_generator.helpers.generator import write_endpoints_to_disk
from api_generator.helpers.log import log
from api_generator.helpers.module_loader import import_submodules
from api_generator.parsers import openapi2

DEFAULT_API_DIRECTORY = site.USER_SITE if site.ENABLE_USER_SITE else get_python_lib()
DEFAULT_API_OUTPUT_DIRECTORY = join(DEFAULT_API_DIRECTORY, "argus_api", "api")


def _load_endpoints(parser: ModuleType, schema_uri: str):
    try:
        endpoints = parser.load(schema_uri)
    except (SSLError, Timeout, ProxyError, MaxRetryError, ssl.SSLError) as error:
        log.error(error)
        log.error("Please check that REQUESTS_CA_BUNDLE is set to the correct certificate if you're behind an SSL terminating proxy.")
        log.error("REQUESTS_CA_BUNDLE=%s" % getenv('REQUESTS_CA_BUNDLE'))
        exit(1)

    return endpoints


def generate_api(schema_uri: str, parser: ModuleType = None):
    """Regenerates the API into the default location

    :param parser: Parser to parse the definitions with
    :param str schema_uri: Path or URL to schema
    """
    parser = parser or openapi2

    log.info("Generating API modules using %s..." % schema_uri)
    endpoints = _load_endpoints(parser, schema_uri)

    log.info("Creating module directory...")
    if not exists(DEFAULT_API_OUTPUT_DIRECTORY):
        makedirs(DEFAULT_API_OUTPUT_DIRECTORY)

    log.info("Writing API modules to disk...")
    write_endpoints_to_disk(
        endpoints,
        output=DEFAULT_API_OUTPUT_DIRECTORY,
        with_plugin_decorators=True
    )


def load(api_url: str, swagger_files: list, parser: ModuleType = None, **kwargs) -> ModuleType:
    """Initializes, so that when called, the static API files will
    be generated to disk if they dont already exist, and the module then returned
    to the user. If the api module already exists, return the loaded module.

    :param api_url:
    :param swagger_files: Swagger files to load from the given api UPL
    :param base_url: Base URL to fetch the schema
    :param parser: Optional custom parser module for parsing the schema before writing to disk
    """

    # Attempt to load module api. This module doesn't exist by default,
    # and so on first run, this module will be generated
    parser = parser or openapi2

    try:
        import argus_api.api

        # If the time of generation is older than 2 days,
        # force regeneration
        time_ago = (datetime.now() - datetime.fromtimestamp(argus_api.api.__CREATED_AT__))
        if time_ago.days > 1:
            log.info("Argus API files are %d days old. Re-generating..." % time_ago.days)
            raise ImportError

    except ImportError:
        log.info("No static API files found. Generating them...")
        for schema in swagger_files:
            generate_api("%s%s" % (api_url, schema), parser)
            
    # DONT swallow other exceptions! 
    except Exception as error:
        log.error(error)
        exit(1)

    import argus_api.api
    import_submodules("argus_api.api", exclude_name="test_helpers")
    return argus_api.api
