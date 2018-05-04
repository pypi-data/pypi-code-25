from distutils.core import setup

setup(name='trumpia',
      packages=['trumpia'],
      version='0.1.0.dev4',
      description='Python wrapper for Trumpia API',
      long_description=open('./README.md').read(),
      long_description_content_type="text/markdown",
      license='MIT',
      author='Alex Luis Arias',
      author_email='alex@alexarias.io',
      url='http://github.com/aleksarias/trumpia-python',
      keywords=['trumpia', 'api', 'python'],
      classifiers=[],
      install_requires=[
          'requests',
          'future'
      ],
      zip_safe=False, requires=['requests', 'future'])
