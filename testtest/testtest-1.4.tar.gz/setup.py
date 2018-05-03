from setuptools import setup

setup(
      name='testtest',
      version='1.4',
      py_modules=['using_click'],
      install_requires=[
            'Click',
      ],
      description='Testing Framework',
      url='https://github.com/AlexMcCarroll/pypi_play',
      author='Alex McCarroll',
      author_email='alexandra@mccarrollhk.com',
      license='MIT',
      packages=['testtest'],
      zip_safe=False,
      entry_points={
            'console_scripts': [
                'using_click=using_click:cli',
            ],
      }
      )
