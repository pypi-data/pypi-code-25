from os import path
import re
from setuptools import find_packages, setup

_folder_path = path.dirname(__file__)
_version_path = path.join(_folder_path, 'versiontracker', '_version.py')
with open(_version_path) as f:
    exec(f.read())
version = __version__
git_url = 'https://gitlab.com/gallaecio/versiontracker'


def _long_description():
    with open(path.join(_folder_path, 'README.rst')) as f:
        text = f.read()
    text = re.sub(r'(?s)\nExtending Software Support.*', '', text)
    text = re.sub(r':func:`([^`]+)\s+<[^`>]+>`', r':code:`\1`', text)
    text = re.sub(r':ref:`([^`]+)\s+<[^`>]+>`', r'\1', text)
    text += """

Documentation
-------------

See the complete documentation at
`Read the Docs <https://version-tracker.readthedocs.io/en/latest/>`_.
"""
    return text


setup(
    name='versiontracker',
    version=version,
    description="Web scrapping software to keep track of the latest stable "
                "version of different software.",
    long_description=_long_description(),
    url='http://version-tracker.rtfd.io/',
    download_url='{}/repository/archive.tar.gz?ref=v{}'.format(
        git_url, version),
    author="Adrián Chaves (Gallaecio)",
    author_email='adriyetichaves@gmail.com',
    license='AGPLv3+',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or '
            'later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Archiving :: Packaging',
    ],
    packages=find_packages('.'),
    install_requires=[
        'argcomplete',
        'chardet',
        'cryptography<2',  # https://github.com/scrapy/scrapy/issues/2944
        'pyasn1',  # https://sourceforge.net/p/pyasn1/tickets/5/
        'pyOpenSSL<17.5.0',  # https://github.com/scrapy/scrapy/issues/2944
        'python-dateutil',
        'pyxdg',
        'PyYAML',
        'Scrapy',
        'sphinx-argparse',
        'termcolor',
    ],
    package_data={
        'versiontracker': ['data.yaml'],
    },
    scripts=[
        'bin/versiontracker',
    ],
)
