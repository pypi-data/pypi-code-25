from setuptools import setup, find_packages
setup(
    name = 'solaris_ssh',
    version = '0.1',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'solaris_ssh=solaris_ssh:main',
        ],
    },

    description = 'Python3 library to run SSH in parallel',
    license = 'MIT',
    keywords = 'ssh',
)
