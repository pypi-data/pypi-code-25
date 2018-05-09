from setuptools import setup

setup(
    name='bucket_command_wrapper',
    version='0.3.0',
    description="""Wrapper to facilitate downloading / uploading files
      from buckets (i.e. S3) into containers (i.e. docker) and running an arbitrary command.
      """,
    url='https://github.com/jgolob/bucket_command_wrapper',
    author='Jonathan Golob',
    author_email='j-dev@golob.org',
    license='MIT',
    packages=['bucket_command_wrapper'],
    zip_safe=False,
    install_requires=[
          'boto3',
    ],
    entry_points={
        'console_scripts': ['bucket_command_wrapper=bucket_command_wrapper.bucket_command_wrapper:main'],
    }
)
