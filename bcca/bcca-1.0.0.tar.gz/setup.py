from setuptools import setup

setup(
    name="bcca",
    version="1.0.0",
    description="Helpers from Base Camp Coding Academy",
    packages=["bcca"],
    install_requires=["pytest"],
    entry_points={
        'pytest11': ['bcca = bcca.pytest_plugin'],
    })
