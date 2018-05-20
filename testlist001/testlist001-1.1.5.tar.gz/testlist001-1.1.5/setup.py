from setuptools import setup, find_packages

setup(
	name='testlist001',
	version='1.1.5',
	description='pypi testing',
	py_modules=["potato", "category", "db", "make", "remove", "modify", "page", "find", "detail", "plan"],
	entry_points={
	    'console_scripts': [
	        'potato=potato:run',
	        'potatofield=potato:run'
	    ]
	}
)
