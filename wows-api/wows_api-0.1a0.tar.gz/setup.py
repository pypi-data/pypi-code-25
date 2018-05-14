from setuptools import setup


setup(
    name='wows_api',
    version='0.1a',
    packages=['wows_api'],
    install_requires=['requests'],
    url='https://github.com/pachkun/wows_api',
    author='pachkun',
    author_email='pachkunishka@gmail.com',
    description='Работа с api world of warship',
    python_requires='>=3.6',
    include_package_data=True
)
