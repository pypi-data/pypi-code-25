import io
import os
from setuptools import setup


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


with io.open('README.rst', encoding='utf-8') as fp:
    description = fp.read()
req = ['markdown',
       'PyYAML',
       'requests']
setup(name='cacheflow',
      version='0.1',
      packages=['cacheflow'],
      entry_points={
          'console_scripts': [
              'cacheflow = cacheflow.main:main',
              'noteflow = cacheflow.noteflow:main']},
      install_requires=req,
      description="Caching Workflow Engine",
      long_description=description,
      author="Remi Rampin",
      author_email='remi.rampin@nyu.edu',
      maintainer="Remi Rampin",
      maintainer_email='remi.rampin@nyu.edu',
      url='https://gitlab.com/remram44/cacheflow',
      project_urls={
          'Source': 'https://gitlab.com/remram44/cacheflow',
          'Tracker': 'https://gitlab.com/remram44/cacheflow/issues',
          'Say Thanks': 'https://saythanks.io/to/remram44',
      },
      license='BSD-3-Clause',
      keywords=['cache', 'workflow', 'pipeline', 'dataflow', 'flow',
                'execution', 'engine'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Programming Language :: SQL',
          'Programming Language :: Unix Shell',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Interpreters',
          'Topic :: Text Processing :: Markup',
          'Topic :: Utilities',
      ])
