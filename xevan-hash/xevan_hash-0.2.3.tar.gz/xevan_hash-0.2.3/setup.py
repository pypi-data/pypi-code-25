import setuptools
from distutils.core import setup, Extension

xevan_hash_module = Extension('xevan_hash',
                                 sources = ['xevanmodule.c',
                                            'xevanhash.c',
                                            'sha3/blake.c',
                                            'sha3/bmw.c',
                                            'sha3/groestl.c',
                                            'sha3/skein.c',
                                            'sha3/jh.c',
                                            'sha3/keccak.c',
                                            'sha3/luffa.c',
                                            'sha3/cubehash.c',
                                            'sha3/shavite.c',
                                            'sha3/simd.c',
                                            'sha3/echo.c',
                                            'sha3/hamsi.c',
                                            'sha3/fugue.c',
                                            'sha3/shabal.c',
                                            'sha3/whirlpool.c',
                                            'sha3/sph_sha2big.c',
                                            'sha3/haval.c'],
                               include_dirs=['.', './sha3'])

setup (name = 'xevan_hash',
       version = '0.2.3',
       description = 'Binding for xevan proof of work hashing.',
       long_description=open('README.md').read(),
       long_description_content_type="text/markdown",
       url = 'https://github.com/ddude1/Xevan_in_Python.git',
       download_url = 'https://github.com/ddude1/Xevan_in_Python/archive/0.2.tar.gz',
       classifiers=[
   		'Development Status :: 5 - Production/Stable',
   		'Programming Language :: Python',
   	],
       ext_modules = [xevan_hash_module])
