import os.path
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dployr',
    version='1.0.0',
    description='Blog deployment script',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dutch/dployr',
    author='Chris Lamberson',
    author_email='clamberson@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='development',
    packages=find_packages(),
    install_requires=['flask'],
    entry_points={
        'console_scripts': [
            'dployr=dployr:main'
        ]
    },
    project_urls={
        'Bug Reports': 'https://github.com/dutch/dployr/issues',
    }
)
