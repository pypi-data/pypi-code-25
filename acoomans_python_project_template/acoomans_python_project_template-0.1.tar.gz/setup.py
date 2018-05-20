from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
	long_description = f.read()
	
with open(path.join(here, 'requirements.txt')) as f:
	requirements = f.read()

setup(
	name='acoomans_python_project_template',
	version=0.1,
	author='Arnaud Coomans',
	author_email='arnaud.coomans@gmail.com',
	description='A description for my python project',
	long_description=long_description,
	url='https://github.com/acoomans/python_project_template',
	license='BSD',
    platforms='any',
	keywords=[
		'a',
		'b',
		'c'
	],
	install_requires=requirements,
	scripts=['scripts/myscript.py'],
	packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    test_suite='tests.test_project',
)