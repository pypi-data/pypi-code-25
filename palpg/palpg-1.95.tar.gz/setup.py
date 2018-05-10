from setuptools import setup

with open('README.txt') as file:
    long_description = file.read()

setup(name='palpg',
      version='1.95',
      description='Postgres Wrapper Class using psycopg2',
      long_description=long_description,
      url='https://github.com/ipal0/palpg',
      author='Pal',
      author_email='ipal0can@gmail.com',
      license='GPL',
      install_requires=[ 'psycopg2-binary', ],
      python_requires='>=3',
      packages=['palpg'])
