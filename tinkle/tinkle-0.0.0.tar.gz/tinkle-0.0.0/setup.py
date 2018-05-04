from distutils.core import setup

setup(
    name = 'tinkle',
    description = 'Data Simplified',
    packages = ['tinkle'],
    license = "Apache License, Version 2.0",
    keywords = ['NLP', 'CL', 'natural language processing',
              'computational linguistics', 'parsing', 'tagging',
              'tokenizing', 'syntax', 'linguistics', 'language',
              'natural language', 'text analytics'],
    maintainer = "Liling Tan",
    classifiers = [
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3.6',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Human Machine Interfaces',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Text Processing',
    ],
    package_data={'tinkle': ['data/corpora/*.tsv', 'data/models/**/*.pickle']},
    install_requires = ['nltk']
)
