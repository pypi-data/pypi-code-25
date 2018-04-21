# encoding: utf-8

'''
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
'''

from __future__ import print_function, unicode_literals

import errno
import os
import sys

import setuptools
import subprocess


class ReleaseCommand(setuptools.Command):
    # command class must provide 'user_options' attribute (a list of tuples)
    user_options = []

    def __init__(self, dist, **kw):
        self.__version = kw.pop("version")

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import re
        from pkg_resources import parse_version
        from pkg_resources.extern.packaging.version import Version, LegacyVersion

        if not isinstance(parse_version(self.__version), Version):
            sys.stderr.write("invalid version string: {}\n".format(self.__version))
            sys.exit(errno.EINVAL)

        tag = "v{}".format(self.__version)

        print("Pushing git tags: {}".format(tag))

        print("git tag {}".format(tag), shell=True)
        print("git push --tags", shell=True)
        """
        return_code = subprocess.call("git tag {}".format(tag), shell=True)
        if return_code != 0:
            sys.exit(return_code)

        return_code = subprocess.call("git push --tags", shell=True)
        if return_code != 0:
            sys.exit(return_code)
        """

        version_regexp = re.compile(re.escape(self.__version))
        upload_file_list = []
        dist_dir = "dist"

        for filename in os.listdir(dist_dir):
            if not version_regexp.search(filename):
                continue

            upload_file_list.append(os.path.join(dist_dir, filename))

        if not upload_file_list:
            sys.stderr.write("file not found to upload\n")
            sys.exit(errno.ENOENT)

        print("twine upload {:s}".format(" ".join(upload_file_list)), shell=True)
        #subprocess.call("twine upload {:s}".format(" ".join(upload_file_list)), shell=True)
