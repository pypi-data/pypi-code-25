from setuptools import setup, find_packages

entries = [
    'csvmerge = pkit.cmd.csvmerge',
    'csvfilter = pkit.cmd.csvfilter',
    'findhash = pkit.cmd.findhash',
    'finddupes = pkit.cmd.finddupes',
    'mkqtproj = pkit.cmd.mkqtproj'
]

setup(
    name='pkit',
    version='0.1.1',
    license='BSD License',
    description='various command line utilities and scripts',
    url='https://www.github.com/redouane/pkit',
    author='Redouane Zait',
    author_email='redouanezait@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas',
    ],

    extras_require={
        'dev':[
            'sphinx'
        ]
    },

    entry_points={
        'pkit.commands': entries,

        'console_scripts': [
            'pkit = pkit.__main__:main'
        ]
    },

    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],

)
