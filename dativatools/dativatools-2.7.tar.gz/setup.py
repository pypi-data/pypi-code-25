from setuptools import setup

setup(name='dativatools',
      version='2.7',
      description='Useful tools when building data pipelines',
      url='https://github.com/dativa4data/dativatools/tree/master',
      author='The Dativa Team',
      author_email='hello@dativa.com',
      license='MIT',
      zip_safe=False,
      packages=['dativatools',
                'tests'],
      install_requires=[
          'boto>=2.48.0',
          'boto3>=1.4.4',
          'botocore>=1.5.80',
          'chardet>=3.0.4',
          'pandas>=0.18.0',
          'paramiko>=2.2.1',
          'patool>=1.12',
          'psycopg2>=2.7.3.1',
          'pexpect>=4.2.1'
      ],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Topic :: Scientific/Engineering',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6'],
      keywords='dativa',)
