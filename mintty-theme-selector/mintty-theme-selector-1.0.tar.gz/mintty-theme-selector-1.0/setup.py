from setuptools import setup, find_packages

setup(
    name='mintty-theme-selector',
    version='1.0',
    description='Command-line theme selector for mintty',
    url='https://github.com/kohanyirobert/mintty-theme-selector',
    author='Kohányi Róbert',
    author_email='kohanyi.robert@gmail.com',
    license='WTFPL',
    keywords='mintty theme command-line',
    packages=find_packages(),
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'mts=main:main',
        ],
    },
)
