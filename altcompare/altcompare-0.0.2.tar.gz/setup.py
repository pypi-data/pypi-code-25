

from setuptools import setup, find_packages

setup(
    name='altcompare',
    version='0.0.2',
    description='Data Compare Utility in Python',
    url='https://github.com/pvparuchuri/altcompare',
    author='Venkata Paruchuri',
    classifiers=[  
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    python_requires='>=3',
    keywords='Data Comparison odbc compare',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  
    project_urls={
        'Bug Reports': 'https://github.com/pvparuchuri/altcompare/issues',
        'Source': 'https://github.com/pvparuchuri/altcompare/',
    },
)