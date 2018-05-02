"""reproduce setup.py."""
from setuptools import setup

README = open('README.rst').read()

setup(
    name='reproduce',
    use_scm_version={'version_scheme': 'post-release',
                     'local_scheme': 'node-and-date'},
    setup_requires=['setuptools_scm'],
    description='Computational reproduction library.',
    long_description=README,
    maintainer='Rich Sharp',
    maintainer_email='richpsharp@gmail.com',
    url='https://bitbucket.org/richsharp/reproduce',
    packages=['reproduce'],
    package_dir={
        'reproduce': 'src'
    },
    license='BSD',
    keywords='computing reproduction',
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2 :: Only',
        'License :: OSI Approved :: BSD License'
    ])
