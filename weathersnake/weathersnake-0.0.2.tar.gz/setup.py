from setuptools import setup, find_packages

setup(
    name='weathersnake',
    version='0.0.2',
    description='Python tool to find the weather',
    author='Eric Cheatham',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'googlemaps',
        'requests[security]',
    ],
    entry_points={
        'console_scripts': ['weathersnake = weather.cli:main']
    }
)
