from setuptools import setup, find_packages

setup(
      name='testtest',
      version='1.7',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
            'emoji',
            'Click',
      ],
      description='Testing Framework',
      url='https://github.com/AlexMcCarroll/pypi_play',
      author='Alex McCarroll',
      author_email='alexandra@mccarrollhk.com',
      license='MIT',
      zip_safe=False,
      entry_points={
            'console_scripts': [
                'using_click=testtest.scripts.using_click:cli',
            ],
      }
      )
