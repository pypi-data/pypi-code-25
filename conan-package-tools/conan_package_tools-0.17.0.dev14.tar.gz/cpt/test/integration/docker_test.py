import unittest

from future.moves import sys

from conans.client import tools
from cpt.test.integration.base import BaseTest
from cpt.packager import ConanMultiPackager


class DockerTest(BaseTest):

    #@unittest.skipUnless(sys.platform.startswith("linux"), "Requires Linux")
    def test_docker(self):
        conanfile = """from conans import ConanFile
import os

class Pkg(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

"""
        self.save_conanfile(conanfile)
        with tools.environment_append({"CONAN_USE_DOCKER": "1"}):
            self.packager = ConanMultiPackager("--build missing -r conan.io",
                                               "lasote", "mychannel",
                                               gcc_versions=["6"],
                                               archs=["x86"],
                                               build_types=["Release"],
                                               reference="zlib/1.2.2")
            self.packager.add_common_builds()
            self.packager.run_builds(1, 1)
