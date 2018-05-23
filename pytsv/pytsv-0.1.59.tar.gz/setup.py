import setuptools

"""
The documentation can be found at:
http://setuptools.readthedocs.io/en/latest/setuptools.html
"""
setuptools.setup(
    # the first three fields are a must according to the documentation
    name='pytsv',
    version='0.1.59',
    packages=[
        'pytsv',
        'pytsv.endpoints',
    ],
    # from here all is optional
    description='pytsv is a module to help with all things TSV',
    long_description='pytsv is a module to help with all things TSV',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    maintainer='Mark Veltzer',
    maintainer_email='mark.veltzer@gmail.com',
    keywords=[
        'python',
        'tsv',
        'format',
        'csv',
    ],
    url='https://veltzer.github.io/pytsv',
    download_url='https://github.com/veltzer/pytsv',
    license='MIT',
    platforms=[
        'python2',
    ],
    install_requires=[
        'pytconf',
        'tqdm',
        'pyanyzip',
        'numpy',
        'pandas',
        'pylogconf',
        'attrs',
    ],
    extras_require={
        ':python_version == "2.7"': ['futures'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    data_files=[
    ],
    entry_points={'console_scripts': [
        'pytsv=pytsv.endpoints.main:main',
    ]},
    python_requires='>=2.7',
)
