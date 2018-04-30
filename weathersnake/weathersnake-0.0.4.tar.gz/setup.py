from setuptools import setup, find_packages


setup_args = dict(
    name='weathersnake',
    version='0.0.4',
    description='Python tool to find the weather',
    author='Eric Cheatham',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'googlemaps',
        'requests[security]',
    ],
    entry_points={
        'console_scripts': [
            'weathersnake = weather.cli:main'
        ]
    }
)

if __name__ == '__main__':
    setup(**setup_args)
