from setuptools import setup


setup(name='sp-ccrawl',
      version='0.3',
      description='The base for commoncrawl analysis based on sparkcc',
      long_description=("The base for commoncrawl analysis based on sparkcc "
                        "with added file selection base on time range"),
      url='http://github.com/rtaubes/spcc',
      keywords='spark commoncrawl',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
      ],
      author='Roman Taubes',
      author_email='roman.taubes@gmail.com',
      license='MIT',
      packages=['sp_ccrawl'],
      # possibilities: package_dir=['...'], package_data={'mypkg': ['...']}
      install_requires = [
          'boto3', 'botocore', 'warcio'
      ],
#       test_suite='nose.collector',
#       tests_require=['nose', 'nose-cover3'],
#       entry_points={
#           'console_scripts': ['funniest-joke=funniest.command_line:main'],
#       },
      include_package_data=True,  # see Manifest.in
      zip_safe=False)
