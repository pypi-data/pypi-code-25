from setuptools import setup

setup(name='recommend_engine',
      version='1.0',
      py_modules=['main'],
      install_requires=['numpy', 'matplotlib'],
      url='https://github.com/ogura-edu/recommend-engine',
      author='Masayoshi Ogura',
      author_email='ogura176578@gmail.com',
      entry_points={
          'console_scripts': ['recommend = main:main']
      })
