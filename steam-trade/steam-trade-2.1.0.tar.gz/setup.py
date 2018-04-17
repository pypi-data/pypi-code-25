from setuptools import setup

setup(
    name='steam-trade',
    version='2.1.0',
    packages=['pytrade'],
    url='https://github.com/Zwork101/steam-trade',
    license='MIT',
    author='Zwork101',
    author_email='zwork101@gmail.com',
    description='An Asynchronous, event based steam trade library',
    install_requires=["pyee", "aiohttp", "steamid", "rsa", "bs4"],
)
