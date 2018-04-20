from setuptools import setup, find_packages

setup(
    name             = 'sj_test',
    version          = '1.2',
    py_modules       = ["sj"],
    description      = 'SJ Python Source Code',
    author           = 'mokuzin21',
    author_email     = 'songew@gmail.com',
    url              = 'https://github.com/rampart81/pyquibase',
    download_url     = 'https://githur.com/rampart81/pyquibase/archive/1.0.tar.gz',
    install_requires = [ ],
    packages         = find_packages(exclude = ['docs', 'tests*']),
    keywords         = ['smartlamp'],
    python_requires  = '>=3',
    package_data     = {},
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)