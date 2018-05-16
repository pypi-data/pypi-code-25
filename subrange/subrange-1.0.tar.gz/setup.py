import setuptools


try:
    with open("README.rst") as f:
        long_description = f.read()
except:
    long_description = None

setuptools.setup(
    name="subrange",
    version="1.0",
    description="Subrange data type",
    url="https://github.com/xoiss/python-subrange",
    author="Alexander A. Strelets",
    author_email="StreletsAA@gmail.com",
    license="Public Domain",
    download_url="https://github.com/xoiss/python-subrange",
    long_description=long_description,
    platforms=['Linux'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=["subrange"],
)
