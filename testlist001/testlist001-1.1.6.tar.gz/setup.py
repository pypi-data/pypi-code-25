from setuptools import setup, find_packages

setup(
	name='testlist001',
	version='1.1.6',
	description='pypi testing',
	packages=['potatofield'],
	entry_points={
	    'console_scripts': [
	        'potato=potatofield.potato:run',
	        'potatofield=potatofield.potato:run'
	    ]
	}
)
