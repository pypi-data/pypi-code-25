from setuptools import setup, find_packages

setup(
	name='pipTestPackage',
	version='0.0.2',
	url='https://github.com/goodboychan/pipTestPackage',
	license='MIT',
	author='Chanseok Kang',
	author_email='chanseok.kang@lge.com',
	description='Test Packaging',
	keywords='test package development',
	packages=find_packages(),
	install_requires=['numpy', 'matplotlib'],
	zip_safe=False,
)
