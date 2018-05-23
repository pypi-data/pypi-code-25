from distutils.core import setup, Extension

x13_hash_module = Extension('x13_hash',
                               sources = ['x13module.c',
                                          'x13.c',
                                          'x13.h',
										  'sha3/blake.c',
										  'sha3/bmw.c',
										  'sha3/groestl.c',
										  'sha3/jh.c',
										  'sha3/keccak.c',
										  'sha3/skein.c',
										  'sha3/cubehash.c',
										  'sha3/echo.c',
										  'sha3/luffa.c',
										  'sha3/simd.c',
                                                                                  'sha3/hamsi.c',
                                                                                  'sha3/hamsi_helper.c',
                                                                                  'sha3/fugue.c',
										  'sha3/shavite.c'],

                               include_dirs=['.', './sha3'])

setup (name = 'x13_hash',
       version = '2.1.0',
       description = 'Bindings for proof of work used by x13',
       maintainer = 'Sean McCaffery',
       maintainer_email = 'john.smart9@gmail.com',
       long_description = 'Credits: MaruCoin\'s Developer Team: https://github.com/MaruCoinOfficial/x13-hash',
       url = 'https://github.com/MaruCoinOfficial/x13-hash',
       ext_modules = [x13_hash_module])
