from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
found_packages = find_packages(exclude=['contrib', 'example'])

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='revise-x',
    version='0.0.3',
    python_requires='>=3.5',
    description='An exporter for trained neural networks built with keras to work with revise projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/noheltcj/revise-x',

    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # Keywords for the project page
    keywords='revise machine_learning exporter keras',

    packages=found_packages,

    install_requires=[],

    project_urls={
        'Bug Reports': 'https://github.com/noheltcj/revise-x/issues',
        # 'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/noheltcj/revise-x'
    },
)
