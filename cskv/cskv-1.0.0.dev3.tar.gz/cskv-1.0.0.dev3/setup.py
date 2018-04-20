from setuptools import setup, find_packages

long_description='''
CSKV is a python tool too edit INI or RAW config files with a single call.
It can be used as a command-line tool, or it can be imported as a module in
python 2.*.
It does what other similar tools also do, but it also handles indentation,
and automatic file-type recognition (INI or different RAW types).
If the documentation is not clear enough, the source code is relatively short,
so, so any issue can be quickly traced. 
'''

setup(
    name = 'cskv',
    version = '1.0.0.dev3',
    description = 'Config parser for INI and RAW formatted files',
    description_long = long_description,
    long_description_content_type = 'text/plain',
    license = 'GNU General Public License v2 (GPLv2)',
    author = 'Julen Larrucea',
    author_email = 'julen@larrucea.eu',
    url = 'https://github.com/julenl/cskv',
    download_url = 'https://github.com/julenl/cskv/archive/0.1.tar.gz',
    keywords = ['config', 'ini', 'raw', 'parser', 'non-interactive'],
    classifiers = [
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Topic :: System :: Systems Administration",
        ],
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'cskv=cskv.py',
            ],
        },
)
