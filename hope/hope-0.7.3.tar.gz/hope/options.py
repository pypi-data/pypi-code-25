# Copyright (c) 2013 ETH Zurich, Institute of Astronomy, Lukas Gamper <lukas.gamper@usystems.ch>

from __future__ import print_function, division, absolute_import, unicode_literals

import subprocess
from distutils.version import StrictVersion
from distutils.sysconfig import customize_compiler
from distutils import sysconfig

from hope.exceptions import UnsupportedCompilerException

CXX_FLAGS = {
    "clang": ["-Wall", "-Wno-unused-variable", "-march=native", "-stdlib=libc++", "-std=c++11",
              "-Wno-unreachable-code"],
    "icc": ["-Wall", "-Wno-unused-variable", "-march=native", "-stdlib=libc++", "-std=c++11",
            "-Wno-unreachable-code"],
    "gcc-mac": ["-Wall", "-Wno-unused-variable", "-std=c++11", "-msse4.2", "-Wno-unreachable-code"],
    "gcc-linux": ["-Wall", "-Wno-unused-variable", "-std=c++11", "-Wno-unreachable-code"]
}

DARWIN_KEY = "Darwin"
LINUX_KEY = "Linux"

GCC_CLANG_VERSION = "4.2.1"  # always returned by clang -dumpversion
MIN_GCC_VERSION = "4.7.0"
SUPPORTED_VERSIONS = {"gcc": MIN_GCC_VERSION,
                      "gcc-linux": MIN_GCC_VERSION,
                     }


def enableUnsaveMath():
    """
    Enable the fast-math and associative-math flags in the c++ compiler.

    .. warning::
        using these flags, ``nan`` and ``inf`` are not propageted properly.
        Only use these flags if you know what you are doing!
    """
    from . import config
    config.cxxflags += ["-fassociative-math", "-ffast-math"]


# Disable faster but unsecure Math
def disableUnsaveMath():
    """
    Disable the fast-math and associative-math flags in the c++ compiler.
    """
    from . import config

    flags = config.cxxflags
    for flag in ("-ffast-math", "-fassociative-math"):
        if flag in flags:
            flags.remove(flag)


# HOPE requires the compiler to compile with c++11 features enabled
def get_cxxflags():

    # late imports here make mocking in tests possible:
    from platform import system
    from distutils.ccompiler import new_compiler

    if system() == DARWIN_KEY:
        CXX_FLAGS["gcc"] = CXX_FLAGS["gcc-mac"]
        CXX_FLAGS["cc"] = CXX_FLAGS["clang"]
        CXX_FLAGS["c++"] = CXX_FLAGS["clang"]
    elif system() == LINUX_KEY:
        CXX_FLAGS["gcc"] = CXX_FLAGS["gcc-linux"]
        CXX_FLAGS["cc"] = CXX_FLAGS["gcc"]
        CXX_FLAGS["c++"] = CXX_FLAGS["gcc"]
    else:
        raise UnsupportedCompilerException("System: %s is not supported by HOPE" % system())

    sysconfig.get_config_vars()  # init vars
    compiler = new_compiler()
    customize_compiler(compiler)
    compiler_name = compiler.compiler[0].split("/")[-1]

    if compiler_name not in CXX_FLAGS.keys():  # trying to support x86_64-linux-gnu-gcc
        compiler_name = "gcc-linux" if compiler_name.find("gcc") > -1 else compiler_name

    _check_version(compiler_name, compiler.compiler[0])

    for name, flags in CXX_FLAGS.items():
        if compiler_name.startswith(name):
            return flags
    raise UnsupportedCompilerException("Unknown compiler: {0}".format(compiler_name))


def _check_version(compiler_name, compiler_exec):
    if compiler_name in SUPPORTED_VERSIONS.keys():
        flags = ('-dumpversion', '-dumpfullversion')
        for flag in flags:
            try:
                sversion = subprocess.check_output(
                    compiler_exec + ' ' + flag, shell=True).decode().rstrip()
                version = str(StrictVersion(sversion))
                break
            except ValueError:
                continue
        else:
            raise ValueError(
                'gcc did not provide usefull version info for any of the flags {}'.format(flags))

        if version < StrictVersion(SUPPORTED_VERSIONS[compiler_name]):
            # dont raise an exception if its gcc proxied clang
            if version != StrictVersion(GCC_CLANG_VERSION):
                msg = ("Compiler '%s' with version '%s' is not supported. Minimum version is '%s'"
                       % (compiler_exec, sversion, SUPPORTED_VERSIONS[compiler_name]))
                raise UnsupportedCompilerException(msg)
