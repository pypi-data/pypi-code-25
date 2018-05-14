"""Setup file"""

from setuptools import setup

setup(
    name='lektor-make',
    version='0.2',
    author='Barnaby Shearer',
    author_email='b@zi.is',
    url='http://github.com/BarnabyShearer/lektor-make',
    license='MIT',
    py_modules=['lektor_make'],
    description='Run `make lektor` for custom build systems.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Framework :: Lektor',
        'Environment :: Plugins',
    ],
    entry_points={'lektor.plugins': [
        'make = lektor_make:MakePlugin',
    ]})
