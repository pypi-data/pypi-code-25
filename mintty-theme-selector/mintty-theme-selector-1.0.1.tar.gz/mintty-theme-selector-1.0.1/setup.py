from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='mintty-theme-selector',
    version='1.0.1',
    description='Command-line theme selector for mintty',
    long_description=long_description,
    long_description_content_type='text/markdown',
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
