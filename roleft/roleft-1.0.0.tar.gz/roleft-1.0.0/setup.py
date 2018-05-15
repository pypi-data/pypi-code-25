from setuptools import setup, find_packages

setup(
    name = 'roleft',
    version = '1.0.0',
    keywords = 'roleft utils',
    description = 'roleft.com 的基础工具集合',
    license = 'MIT License',
    url = 'https://roleft.com',
    install_requires = ['pycryptodome>=3.6.1'],
    author = 'wenzd',
    author_email = 'october731@163.com',
    packages = find_packages(exclude=['ez_setup', 'examples', 'tests']),
    python_requires='>=3.5',
)