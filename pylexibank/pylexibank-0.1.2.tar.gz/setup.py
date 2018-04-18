from setuptools import setup, find_packages


def read(fname):
    with open(fname) as fp:
        return fp.read()


setup(
    name='pylexibank',
    version='0.1.2',
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    description='Python library implementing the lexibank workbench',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    keywords='',
    license='Apache 2.0',
    url='https://github.com/lexibank/pylexibank',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'lexibank=pylexibank.__main__:main',
        ],
        'pytest11': [
            'pytest_lexibank = pylexibank.pytest_plugin',
        ]
    },
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=[
        'six',
        'attrs',
        'pycldf>=1.1.1',
        'clldutils',
        'pyglottolog',
        'pyconcepticon',
        'pyclpa',
        'segments',
        'lingpy',
        'appdirs',
        'requests',
        'termcolor',
        'gitpython',
        'tqdm',
        'xlrd',
        'prompt_toolkit~=1.0',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'mock',
            'pytest>=3.1',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
