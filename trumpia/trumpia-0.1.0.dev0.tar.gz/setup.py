from distutils.core import setup
import versioneer


setup(name='trumpia',
      packages=['trumpia'],
      version='0.1.0.dev0',
      description='Python wrapper for Trumpia API',
      license='MIT',
      author='Alex Luis Arias',
      author_email='alex@alexarias.io',
      url='http://github.com/aleksarias/trumpia-python',
      keywords=['trumpia', 'api', 'python'],
      setup_requires=['setuptools-git-version'],
      classifiers=[],
      zip_safe=False)
