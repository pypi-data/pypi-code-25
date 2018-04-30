import os
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

os.environ['CC'] = 'gcc-7'
os.environ['CXX'] = 'g++-7'
# os.environ['CFLAGS'] = '-stdlib=libstdc++'

setup(
    name='cluster_cuda',
    ext_modules=[
        CUDAExtension(
            name='cluster_cuda',
            sources=['cluster.cpp', 'cluster_kernel.cu'],
            # extra_compile_args=['-std=c++11'],
        )
    ],
    cmdclass={'build_ext': BuildExtension},
)
