from setuptools import setup, find_packages


setup(
    name='pykonkeio',
    version='1.0.1',
    keywords=('konke', 'iot'),
    description='Python library for interfacing with konke smart appliances',
    long_description=open('README.md', 'rt').read(),
    author='jedmeng',
    author_email='jedm@jedm.cn',
    url='https://github.com/jedmeng/python-konekeio',
    license='MIT',
    install_requires=[
        'pycrypto'
    ],
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.5',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'konekeio=konekeio.__main__:main',
        ]
    },
)
