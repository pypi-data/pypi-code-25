from setuptools import setup

version = '0.0.1'
name = 'md2tex'
short_description = '`md2tex` is a package which convert markdown to TeX.'
long_description = """\
`md2tex` is a package which convert markdown to TeX.
::

   $ ls
   00.md 01.md
   $ md2tex
   Output 00.tex
   Output 01.tex

Requirements
------------
* Python 3

Features
--------
* nothing

Rule
--------
* Chapter: `# title[*][#label]`
* Introduction: `# はじめに`
* Bibliography: `# 参考文献`
* Section: `## title[*][#label]`
* Subsection: `**title[*]**`
* Figure `![caption#fig:label~width](URI)`
* Index: `<#keyword｜ruby>`
* Reference: `<@label>`
* Raw text: `<=text>`
* Footnote: `<%contents>`
* Column width: `<~width>`

Setup
-----
::

   $ pip install md2tex

History
-------
0.0.1 (2018-4-13)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Software Development",
   "Topic :: Scientific/Engineering",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    py_modules=['md2tex'],
    keywords=['md2tex',],
    author='Saito Tsutomu',
    author_email='tsutomu.saito@beproud.jp',
    url='https://pypi.python.org/pypi/md2tex',
    license='PSFL',
    entry_points={
            'console_scripts':[
                'md2tex = md2tex:main',
            ],
        },
)