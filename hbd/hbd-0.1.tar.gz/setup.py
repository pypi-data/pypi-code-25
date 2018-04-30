from setuptools import setup

setup(
    name='hbd',
    description='API and CLI for Humble Bundle downloads',
    author='BitLooter',
    author_email='pwnzerdragoon+pypihbd@gmail.com',
    version='0.1',
    py_modules=['hbd', 'cli'],
    install_requires=[
        'appdirs',
        'click',
        'colorama',
        'requests',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'hbd=cli:cli'
        ]
    },
    license='LGPL3'
)
