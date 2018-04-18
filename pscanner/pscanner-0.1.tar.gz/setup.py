from setuptools import setup, find_packages

setup(
    name = 'pscanner',
    version = '0.1',
    author = 'Ammad Khalid',
    author_email = 'ammadkhalid12@gmail.com',
    packages = find_packages(),
    url = 'https://github.com/Ammadkhalid/pscanner',
    install_requires = ['requests'],
    python_requires = '>= 3',
    entry_points = {
        'console_scripts': ['pscanner = pscanner.cli.__main__:main'],
    }
)