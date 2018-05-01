from setuptools import setup

setup(name='e80analysis',
      version='0.1',
      description='A tool to find the equivalent Cooper E-loading for a user-specified train configuration.',
      url='https://github.com/rspears74/e80analysis',
      author='Randall Spears',
      author_email='rspears690@gmail.com',
      license='MIT',
      packages=['e80analysis'],
      install_requires=[
          'matplotlib',
      ],
      include_package_data=True,
      zip_safe=False)