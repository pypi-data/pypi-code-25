from setuptools import setup

setup(
    name="trf2csv",
    version="0.2.0",
    author="Simon Biggs",
    author_email="mail@simonbiggs.net",
    description="A placeholder",
    packages=[
        "trf2csv"
    ],
    entry_points={
        'console_scripts': [
            'trf2csv=trf2csv:main',
        ],
    },
    license='AGPL3+',
    install_requires=[
        'numpy',
        'pandas',
        'attrs'
    ],
    include_package_data=True
)
