from setuptools import setup

setup(name='genespider4python',
      version='0.1',
      description='The python translation of the MATLAB genespider package.',
      url='https://gitlab.com/Xparx/genespider4python',
      author='Andreas Tjärnberg',
      author_email='andreas.tjarnberg@fripost.org',
      license='LGPL',
      packages=['gspy'],
      python_requires='>=3',
      install_requires=[
          'numpy',
          'pandas',
          'sklearn',
          'scipy',
      ],
      zip_safe=False)
