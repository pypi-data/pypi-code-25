from setuptools import setup

with open('README.rst') as file:
	long_description = file.read()

setup(name='pysc1',
	version='0.0.4',
	description='StarCraft I Learning Environment',
	long_description=long_description,
	url='https://github.com/bboyseiok/pysc1',
	author='bboyseiok',
	author_email='bboyseiok@deepest.ai',
	licence='BSP',
	packages=['pysc1'],
	zip_safe=False)