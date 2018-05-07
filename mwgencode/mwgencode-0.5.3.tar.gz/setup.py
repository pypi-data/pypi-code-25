# from distutils.core import setup
from setuptools import setup

setup(
    name='mwgencode',
    version='0.5.3',
    author='cxhjet',
    author_email='13064576@qq.com',
    py_modules=['manage'],
    packages=['gencode',
              'gencode.gencode',
              'gencode.importxmi',
              'gencode.importmdj',
              'gencode.gencode.sample',
              'gencode.gencode.template',
              'gencode.gencode.template.tests',
              'gencode.gencode.sample.seeds'
           ],
    package_data={
        '': ['*.*']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'flask>=0.11.1'
    ],
    # 可以在cmd 执行产生代码
    entry_points={
        'console_scripts': ['gencode=manage:main']
    }
)
