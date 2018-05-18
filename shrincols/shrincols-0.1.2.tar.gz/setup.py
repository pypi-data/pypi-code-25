from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='shrincols',
    description='Tool for fit string to a fixed number of cols.',
    long_description=readme,
    author='Thiago Melo',
    author_email='thiago.lc.melo@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[],
    entry_points={
        'console_scripts': [
            'shrincols=shrincols.cli:main',
        ]
    },
    classifiers = [],
    url = 'https://github.com/thiagolcmelo/shrincols',
    download_url = 'https://github.com/thiagolcmelo/shrincols/archive/0.1.1.tar.gz',
    version='0.1.2',
)
