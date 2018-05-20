from setuptools import setup

setup(
	name='testlist001',
	version='1.0.6',
	description='pypi testing',
	py_modules=['potato'],
	entry_points={
	    'console_scripts': [
	        'potato=potato:run',
	        'potatofield=potato:run'
	    ]
	}
)
