from shutil import copy
from os import path
from setuptools import setup

setup(name='pandoc-refheadstyle',
      version='0.2',
      description=('Pandoc filter that sets a a custom style '
                   'for the reference section header.'),
      long_description=('Pandoc filter that sets a custom style '
                        'for the reference section header.'),
      keywords='pandoc reference section header',
      url='https://github.com/odkr/pandoc-refheadstyle/',
      project_urls={'Source': 'https://github.com/odkr/pandoc-refheadstyle/',
                    'Tracker': 'https://github.com/odkr/pandoc-refheadstyle/issues'},
      author='Odin Kroeger',
      author_email='tqxwcv@maskr.me',
      license='MIT',
      python_requires='>=2.7,<4',
      packages=['pandoc_refheadstyle'],
      zip_safe=True,
      install_requires=['panflute'],
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.7',
                   'Environment :: Console',
                   'Operating System :: OS Independent',
                   'Topic :: Text Processing :: Filters'],
      scripts=['scripts/pandoc-refheadstyle'],
      include_package_data=True)

# This is a bit rude, but it should work on many systems.
for i in ('/usr/local/share/man/man1', '/usr/share/man/man1'):
    if path.exists(i):
        try:
            copy(path.join(path.dirname(__file__), 'man/pandoc-refheadstyle.1'), i)
            break
        except Exception:
            pass
