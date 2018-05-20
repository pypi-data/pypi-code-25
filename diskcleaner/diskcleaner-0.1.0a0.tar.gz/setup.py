from setuptools import setup, find_packages

long_description = """
Diskcleaner is a simple utility for cleaning up directories in a volume to
maintain a certain disk usage percentage. It's meant to simply be used from a
cronjob. If a volume can't be cleaned up, the utility will exit non-zero.
"""

install_requires = [
]

test_deps = [
    'pytest'
]

setup(
    name='diskcleaner',
    version='0.1.0.a0',
    description='diskcleaner',
    long_description=long_description,
    author='wilypomegranate',
    author_email='wilypomegranate@users.noreply.github.com',
    packages=find_packages(),
    test_suite='py.test',
    test_require=test_deps,
    extras_require={
        'test': test_deps
    },
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'diskcleaner = diskcleaner.main:main',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Systems Administration',
    ],
)
