from setuptools import setup

setup(name='tronalddump',
      version='0.4',
      description='Donald Trump quotes',
      long_description='Python wrapper for the Tronald Dump API: https://docs.tronalddump.io/',
      long_description_content_type='text/x-rst',
      url='https://bitbucket.org/dabcoder/tronalddump',
      author='David B.',
      author_email='dialindo7@gmail.com',
      keywords='donald trump quotes',
      license='GNU v3',
      packages=['tronalddump'],
      python_requires='>=3',
      install_requires=[
          'requests',
      ],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)