#from distutils.core import setup
from setuptools import setup

from Cython.Build import cythonize

setup (
    name='ik1',
    version='0.1.1',
    description='iks test #1 package',
    author='ik',
    author_email='pedro@gmail.com',
    url='http://google.com',
    license='MIT',
    setup_requires=["setuptools", "cython"],
    install_requires=["setuptools", "cython"],
    ext_modules = cythonize("prms.pyx")
)
