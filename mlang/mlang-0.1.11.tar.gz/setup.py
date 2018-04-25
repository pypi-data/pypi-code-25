# coding: utf-8

from setuptools import setup

setup(
    name='mlang',
    version='0.1.11',
    packages=['mlang.res', 'mlang_client'],
    py_modules=['mlang.config', 'mlang.utils'],
    url='',
    license='MIT',
    author='lishouguang',
    author_email='lishouguang@meizu.com',
    description='mlang client',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=['progressbar2', 'requests-toolbelt', 'numpy', 'cachetools']
)
