from setuptools import setup

try:
    from sphinx.setup_command import BuildDoc
except ImportError:
    BuildDoc = None

from setuptools import setup

setup(
    cmdclass={'build_sphinx': BuildDoc},
    setup_requires=['pbr'],
    pbr=True, )
