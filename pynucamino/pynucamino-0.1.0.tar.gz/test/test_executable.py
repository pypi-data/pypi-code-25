import itertools
import unittest
from unittest import mock

from pynucamino import executable


class TestExecutable(unittest.TestCase):

    # As returned by `platform.system`
    operating_systems = ("Windows", "Darwin", "Linux")

    # As returned by `platform.architecture`
    architectures = (('32bit', None), ('64bit', None))

    # As expected from executable.path
    archnames = {
        ('32bit', None): "386",
        ('64bit', None): "amd64",
    }

    @classmethod
    def resource_path(cls, os, arch):
        os = os.lower()
        archname = cls.archnames[arch]
        if os == 'windows':
            ext = ".exe"
        else:
            ext = ""
        return "bin/nucamino-{os}-{arch}{ext}".format(
            os=os,
            arch=archname,
            ext=ext,
        )

    @classmethod
    def exe_path(cls, os, arch):
        return "/nonsense-root/" + cls.resource_path(os, arch)

    def check_case(self, os, arch):
        pkg_target = "pynucamino.executable.pkg_resources.resource_filename"
        system_target = "pynucamino.executable.platform.system"
        arch_target = "pynucamino.executable.platform.architecture"

        _pkg_mock = mock.patch(
            pkg_target,
            return_value=self.exe_path(os, arch),
        )
        _system_mock = mock.patch(system_target, return_value=os)
        _arch_mock = mock.patch(arch_target, return_value=arch)

        with _pkg_mock as pkg_mock:
            with _system_mock as system_mock:
                with _arch_mock as arch_mock:
                    path = executable.path()
                    self.assertEqual(path, self.exe_path(os, arch))
                    arch_mock.assert_called()
                system_mock.assert_called()
            pkg_mock.assert_called_with(
                "pynucamino",
                self.resource_path(os, arch),
            )

    def test_executable_path(self):
        cases = itertools.product(self.operating_systems, self.architectures)
        for os, arch in cases:
            self.check_case(os, arch)
