from setuptools import setup, find_packages


setup(
    name='pyoppleio',
    version='1.0.4',
    keywords=('pyopple', 'iot'),
    description='Python library for interfacing with opple mobile controlled light',
    long_description=open('README.rst', 'rt').read(),
    author='jedmeng',
    author_email='jedm@jedm.cn',
    url='https://github.com/jedmeng/python-konkeio',
    license='MIT',
    install_requires=[
        'crc16==0.1.1'
    ],
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.5',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pyoppleio=pyoppleio.__main__:main',
        ]
    },
)
