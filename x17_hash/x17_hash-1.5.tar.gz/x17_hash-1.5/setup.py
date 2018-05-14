from distutils.core import setup, Extension

x17_hash_module = Extension(
    'x17_hash',
    sources=[
        'x17module.c',
        'x17.c',
        'x17/blake.c',
        'x17/bmw.c',
        'x17/groestl.c',
        'x17/jh.c',
        'x17/keccak.c',
        'x17/skein.c',
        'x17/cubehash.c',
        'x17/echo.c',
        'x17/luffa.c',
        'x17/simd.c',
        'x17/shavite.c',
        'x17/hamsi.c',
        'x17/fugue.c',
        'x17/shabal.c',
        'x17/whirlpool.c',
        'x17/sha2.c',
        'x17/haval.c',
        'x17/sph_sha2big.c',
    ],
    include_dirs=['.', './x17']
)

setup(
    name='x17_hash',
    version='1.5',
    description='Python X17 hash extension',
    author='cryptolgin',
    author_email='c0re@tutanota.com',
    ext_modules=[x17_hash_module],
)
