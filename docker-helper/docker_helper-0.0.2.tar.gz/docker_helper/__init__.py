import os
import re


def get_current_container_id(read_from='/proc/self/cgroup'):
    """
    Get the ID of the container the application is currently running in,
    otherwise return `None` if not running in a container.

    This is a best-effort guess, based on cgroups.

    :param read_from: the cgroups file to read from (default: `/proc/self/cgroup`)
    """

    if not os.path.exists(read_from):
        return

    with open(read_from, 'r') as cgroup:
        for line in cgroup:
            if re.match('.*/[0-9a-f]{64}$', line.strip()):
                return re.sub('.*/([0-9a-f]{64})$', '\\1', line.strip())


def read_configuration(key, path=None, default=None, single_config=False, fallback_to_env=True):
    """
    Read configuration from a file, Docker config or secret or from the environment variables.

    :param key: the configuration key
    :param path: the path of the configuration file (regular file or Docker config or secret)
    :param default: the default value when not found elsewhere (default: `None`)
    :param single_config: treat the configuration file as containing the full configuration,
        otherwise the file is expected to be a '=' separated key-value list line by line
        (default: `False`)
    :param fallback_to_env: look for the configuration key in the environment variables
        if not found elsewhere (default: `True`)
    """

    if path and os.path.exists(path):
        with open(path, 'r') as config_file:
            if single_config:
                return config_file.read()

            for line in config_file:
                if line.startswith('%s=' % key):
                    return line.split('=', 1)[1].strip()

    if fallback_to_env and key in os.environ:
        return os.environ[key]

    return default

