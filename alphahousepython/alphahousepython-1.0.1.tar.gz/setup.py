# Cython compile instructions

from setuptools import setup, find_packages
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from setuptools import Extension
import numpy
import os
from sys import platform
import sys
import sysconfig
# To build a binary dist that  can be installed 
# python setup.py bdist_wheel

# To build source directory
# python setup.py sdist

# Use python setup.py build_ext --inplace
# to compile


# To clean - python setup.py clean --all

# sys.path.insert(0, os.path.abspath(
#     os.path.join(os.path.dirname(__file__), './alphahousepython/cpp_src')))

cpp_src_dir = "alphahousepython/cpp_src/"
compile_args = ["-std=c++11", "-g"]
link_args = ["-std=c++11", "-g"]


libLocation = ""
# 'magic' to make it play nice with OS X compilers
if sys.platform == "darwin":
    try:
        cc = sysconfig.get_config_var('CC')
        # might still be clang
        if (cc == 'gcc'):
            newCC = os.environ["CC"]
            if (newCC == 'gcc' or newCC == 'g++' or 'clang' in newCC or newCC == ''):
                os.environ["MACOSX_DEPLOYMENT_TARGET"] = "10.9"
                compile_args.append("-stdlib=libc++")
                compile_args.append("-Xpreprocessor")
                compile_args.append("-fopenmp")
                compile_args.append("-lomp")
                link_args.append("-stdlib=libc++")
                link_args.append("-Xpreprocessor")
                link_args.append("-fopenmp")
                link_args.append("-lomp")
                link_args.append("/usr/local/opt/libomp/lib/libgomp.a")
            if (newCC == 'icpc' or newCC == 'icc'):
                compile_args.append("-qopenmp")
                link_args.append("-qopenmp")
            else: #This is probably a custom GCC version
                link_args.append("-fopenmp")
                link_args.append("-lomp")
                compile_args.append("-lomp")
                compile_args.append("-fopenmp")
    except KeyError:
        # default is likely
        os.environ["MACOSX_DEPLOYMENT_TARGET"] = "10.9"
        compile_args.append("-stdlib=libc++")
        link_args.append("-stdlib=libc++")


genotype = Extension(
    libLocation+"gen",
    language="c++",
    include_dirs=[cpp_src_dir+"alphahousenative"],
    extra_compile_args=compile_args,
    extra_link_args=link_args,
    sources=[cpp_src_dir+"gen.pyx", cpp_src_dir+'alphahousenative/IntersectCompare.cpp', cpp_src_dir+'alphahousenative/Genotype.cpp',cpp_src_dir+'alphahousenative/Haplotype.cpp']
)

intersectCompare = Extension(
    libLocation+"PyIntersectCompare",
    language="c++",
    include_dirs=[cpp_src_dir+"alphahousenative"],
    extra_compile_args=compile_args,
    extra_link_args=link_args,
    sources=[cpp_src_dir+"PyIntersectCompare.pyx",
             cpp_src_dir+"alphahousenative/IntersectCompare.cpp"]
)
haplotype = Extension(
    libLocation+"hap",
    language="c++",
    sources=[cpp_src_dir+"hap.pyx", cpp_src_dir+'alphahousenative/Haplotype.cpp', cpp_src_dir+'alphahousenative/Genotype.cpp',
             cpp_src_dir+'alphahousenative/IntersectCompare.cpp', cpp_src_dir+'alphahousenative/HaplotypeLibrary.cpp'],
    include_dirs=[cpp_src_dir+"alphahousenative"],
    extra_compile_args=compile_args,
    extra_link_args=link_args,
)

exceptions = Extension(libLocation+"Exceptions", language="c++", sources=[cpp_src_dir+"Exceptions.py"],
   extra_compile_args=compile_args,
                       extra_link_args=link_args)
pedigree = Extension(
    libLocation+"ped",
    language="c++",
    sources=[cpp_src_dir+"ped.pyx", cpp_src_dir+'alphahousenative/Pedigree.cpp', cpp_src_dir+'alphahousenative/Haplotype.cpp',
             cpp_src_dir+'alphahousenative/IntersectCompare.cpp', cpp_src_dir+'alphahousenative/Genotype.cpp', cpp_src_dir+'alphahousenative/Imputation.cpp'],
    include_dirs=[cpp_src_dir+"alphahousenative"],
    extra_compile_args=compile_args,
    extra_link_args=link_args,
)


haplib = Extension(
    libLocation+"haplib",
    language="c++",
    sources=[cpp_src_dir+"haplib.pyx",
             cpp_src_dir+'alphahousenative/HaplotypeLibrary.cpp', cpp_src_dir+'alphahousenative/Haplotype.cpp', cpp_src_dir+'alphahousenative/IntersectCompare.cpp'],
    include_dirs=[cpp_src_dir+"alphahousenative"],
    extra_compile_args=compile_args,
    extra_link_args=link_args,
)


ext_modules = [exceptions,haplotype, genotype,
               intersectCompare, pedigree, haplib]

setup(
    name="alphahousepython",
    license='GPL',
    author='david',
    author_email='david.wilson@roslin.ed.ac.uk',
    version='1.0.1',
    description='AlphaGenes base library for important genetic data functions',
    long_description="README.md",
    packages=find_packages(exclude=['CMakeFiles', '_pycache', 'docs', 'tests', "tests.*"]),
    ext_modules=cythonize(ext_modules, gdb_debug=True),
    package_data={'alphahousepython': [cpp_src_dir+'*.pxd']},
    include_package_data=True,
    include_dirs=[numpy.get_include()],
    setup_requires=[
        # Note bug noted here: https://github.com/cython/cython/issues/1953 might require cython < 0.26
        "cython >= 0.26",
    ],
)
