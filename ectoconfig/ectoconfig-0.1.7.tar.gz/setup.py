from setuptools import setup, find_packages

__version__ = "0.1.7"
__author__ = "Brian Wiborg"
__author_email__ = "b.wiborg@blunix.org"
__license__ = 'Apache-2.0'

requirements = [
    'pyyaml',
    'toml',
]

requirements_extra = {
    'dev': [
        'flake8',
        'nose2',
        'nose2[coverage_plugin]',
        'parameterized',
        "pylint",
        "twine",
    ],
    'click': [
        'click',
    ],
}

classifiers = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: User Interfaces',
],

package_data = {
    'package': [
        'README.md',
    ],
}

setup(
    name="ectoconfig",
    version=__version__,
    description="Utility for reading configuration from multiple sources.",
    long_description=open("README.rst", 'r').read(),
    # classifiers=classifiers,
    keywords='ecto config configfile config-file env 12-factor argparse optparse',
    url="https://github.com/ectopy/ectoconf",
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    package_data=package_data,
    install_requires=requirements,
    test_suite='nose2.collector.collector',
    tests_require=requirements_extra['dev'],
    extras_require=requirements_extra,
    include_package_data=True,
    zip_safe=True
)
