"""Reads .env files"""

import os
import codecs

__escape_decode = codecs.getdecoder('unicode_escape')


def decode_escaped(escaped):
    """Decodes an escaped ascii string.

    :param escaped: str     - escaped ascii string
    :returns str:           - decoded ascii string
    """
    return __escape_decode(escaped)[0]


def parse_line(line):
    """Parses a line into key=value.

    Empty lines and lines starting with a hash(#) will be skipped.

    :param line: str    - line as string
    :returns tuple:     - key, value
    """
    line = str(line).strip()

    if not line or line.startswith('#') or '=' not in line:
        return None, None

    k, v = line.split('=', 1)

    if k.startswith('export '):
        k.lstrip('export ')

    k, v = k.strip(), v.strip()

    if v:
        v = v.encode('unicode-escape').decode('ascii')
        quoted = v[0] == v[-1] in ['"', "'"]
        if quoted:
            v = decode_escaped(v[1:-1])

    return k, v


def find_nearest_dot_env_file_from(path):
    """Finds the nearest dot-env file upwards the directory tree.

    :param path: str    - relative or absolute path to start searching from.
    :returns NoneType:  - if no dot-env file was found
    :returns str:       - absolute path to nearest dot-env file.
    """
    path = os.path.abspath(path)
    test_path = os.path.join(path, '.env')
    if os.path.exists(test_path):
        return test_path

    if path == os.path.abspath(os.path.sep):
        return None

    return find_nearest_dot_env_file_from(os.path.split(path)[0])


class DotEnvHandler(object):
    """Handler for dot-env files."""

    @staticmethod
    def read_in_config():
        """Loads any .env files if found."""
        c = {}
        dot_env_path = find_nearest_dot_env_file_from(os.path.curdir)
        if dot_env_path:
            with open(dot_env_path, 'r') as fd:
                for line in fd.readlines():
                    k, v = parse_line(line)
                    if k:
                        c[k] = v
        return c
