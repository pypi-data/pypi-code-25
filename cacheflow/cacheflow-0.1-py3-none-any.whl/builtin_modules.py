import os
import tempfile
import requests
from urllib.parse import urlparse

from .base import Module, ModuleLoader


# TODO: More builtin modules
# WriteFile: write a string to a temporary file
# ShellCommand: execute a command
# DockerCommand: execute a Docker container
# FormatString: use Python's format(), or printf-like syntax
# Checksum: check a file's checksum (or add to Download?)


class Download(Module):
    """Downloads a file.
    """
    def __init__(self, headers={}):
        self.headers = headers

    def __call__(self, inputs, temp_dir, **kwargs):
        url, = inputs['url']
        if url.startswith('file://'):
            # Just point directly at file
            # Workflow steps are not supposed to change their inputs
            return {'file': url[7:]}
        else:
            # Download with requests
            r = requests.get(url, headers=self.headers)

            # Create file with correct extension
            path = urlparse(url).path
            extension = os.path.splitext(path)[1]
            fd, filename = tempfile.mkstemp(extension, dir=temp_dir)

            # Write file to disk
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    f.write(chunk)
            os.close(fd)

            return {'file': filename}


class EmptyFile(Module):
    """Gets an empty temporary file.
    """
    def __init__(self, suffix=None):
        self.suffix = suffix

    def __call__(self, inputs, temp_dir, **kwargs):
        fd, filename = tempfile.mkstemp(self.suffix, dir=temp_dir)
        os.close(fd)
        return filename


class BuiltinModulesLoader(ModuleLoader):
    """Built-in modules to do basic things.
    """
    TABLE = dict(
        download=Download,
        empty_file=EmptyFile,
    )

    def get_module(self, module):
        try:
            mod = self.TABLE[module.get('type')]
        except KeyError:
            return None
        else:
            module = dict(module)
            module.pop('type', None)
            return mod(**module)
