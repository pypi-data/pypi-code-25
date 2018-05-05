try:
    import setuptools
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

# This sets up the program's classifiers

classifiers = [
    'Development Status :: 4 - Beta', 'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Operating System :: OS Independent', 'Programming Language :: Python',
    'Programming Language :: JavaScript'
]

classifiers.extend(('Programming Language :: Python :: %s' % x)
                   for x in '2 3 2.7 3.4 3.5 3.6 3.7'.split())


def main():
    # type: () -> None
    install_requires = []
    extras_require = {
        'serialize': ['u-msgpack-python'],
        'crypto': ['cryptography']
    }
    with open('README.rst') as f:
        setup(
            name='predecessor',
            description='A set of useful python classes to inherit from',
            long_description=f.read(),
            version='0.0.2',
            author='Gabe Appleton',
            author_email='gabe@gabeappleton.me',
            url='https://gitlab.com/gappleto97/predecessor',
            license='LGPLv3',
            classifiers=classifiers,
            install_requires=install_requires,
            extras_require=extras_require,
            package_dir={'predecessor': 'py_lib'})


if __name__ == "__main__":
    main()
