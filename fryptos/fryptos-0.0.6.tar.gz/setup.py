"""Set up script"""
from setuptools import setup

def _create_long_desc():
    """Create long description and README formatted with rst."""
    _long_desc = ''
    with open('README.md', 'r') as rf:
        return rf.read()
long_desc = _create_long_desc()

setup(name="fryptos",
      version='0.0.6',
      description='Encrypt files.',
      long_description=long_desc,
      long_description_content_type='text/markdown',
      # long_description="",
      # TODO: Add classifiers.
      classifiers=[
          'Programming Language :: Python'
         ],
      keywords='encrypt file',
      author='Shohei Mukai',
      author_email='mukaishohei76@gmail.com',
      url = 'https://github.com/pyohei/Fryptos',
      packages=['fryptos'],
      entry_points={
          'console_scripts': [
              'fryptos = fryptos.main:execute'],
          },
      license='MIT',
      install_requires=[],
      )

