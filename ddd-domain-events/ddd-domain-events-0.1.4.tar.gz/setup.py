import re
from setuptools import setup


def find_version(filename):
    """Attempts to find the version number in the file names filename.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(filename, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


__version__ = find_version("ddd_domain_events/__init__.py")


def read(filename):
    with open(filename) as fp:
        content = fp.read()
    return content


setup(
    name='ddd-domain-events',
    version=__version__,
    description=['Domain Driven Design: ',
                 'implementation of in memory Cross Cutting domain events infrastructure.'],
    long_description=read('README.rst'),
    author='Victor Klapholz',
    author_email='victor.klapholz@gmail.com',
    url='https://gitlab.com/py-ddd/ddd-domain-events',
    packages=['ddd_domain_events'],
    include_package_data=True,
    license='MIT',
    install_requires=[
    ],
    zip_safe=False,
    keywords=[
        'Domain Driven Design', 'Design Patterns', 'DDD', 'Domain Events', 'Strategic DDD Patterns'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    test_suite='tests'
)
