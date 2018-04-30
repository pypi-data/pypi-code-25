import os

from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CppExtension

os.environ['CC'] = 'clang'
os.environ['CXX'] = 'clang++'

setup(
    name='cluster',
    ext_modules=[CppExtension('cluster_cpu', ['cluster.cpp'])],
    cmdclass={'build_ext': BuildExtension},
)
