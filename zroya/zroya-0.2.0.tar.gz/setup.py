# -*- coding: utf-8 -*-

from shutil import rmtree
from setuptools import setup, Extension, Command
from setuptools.command.build_ext import build_ext
from generate_stubs import GenerateStubFile
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))

# Include path for _zroya module
includes_list = ["./module"]

# List of all *.cpp files in ./module directory
sources_list = []
for root, dirs, files in os.walk("./module"):
    for f in files:
        if os.path.splitext(f)[1] == ".cpp":
            sources_list.append(os.path.join(root, f))

# Python C/CPP Api extension configuration
ext_modules = [
    Extension("_zroya",
              sources=sources_list,
              include_dirs=includes_list,
              extra_compile_args=[
                  "/utf-8"
              ]
    )
]


def findPydFile():
    """
    Return path to .pyd after successful build command.
    :return: Path to .pyd file or None.
    """

    if not os.path.isdir("./build"):
        raise NotADirectoryError

    for path, dirs, files in os.walk("./build"):
        for file_name in files:
            file_name_parts = os.path.splitext(file_name)
            if file_name_parts[1] == ".pyd":
                return path
    return None


class StubsCommand(build_ext):
    def run(self):
        build_ext.run(self)

        print("running stubs")
        # Generate .pyd file for this module
        GenerateStubFile(findPydFile())

class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()

setup(name='zroya',
    version='0.2.0',
    description='Python implementation of Windows notifications.',
    author='Jan Malcak',
    author_email='jan@malcakov.cz',
    license='MIT',
    url='https://malja.github.io/zroya',
    data_files=[
      (".", ["./zroya/zroya.pyi", "./zroya/template_enums.py", "./zroya/zroya.py", "./zroya/dismiss_reason.py"])
    ],
    ext_modules=ext_modules,
    cmdclass={
        "stubs": StubsCommand,
        'upload': UploadCommand,
    }
)
