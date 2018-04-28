from setuptools import setup, find_packages
import os

def long_description():
    with open(os.path.join(".", 'README.md'),
              encoding='utf8') as fp:
        return fp.read()

setup(
    name='add-pinyin-key',
    version='0.0.2',
    description='Add pinyin keys to Chinese bib entries',
    license='MIT',
    packages=find_packages(),
    author='Yao Xu',
    author_email='yaoxu@mail.ustc.edu.cn',
    keywords=['Bib'],
    install_requires=[
        'pypinyin',
        'bibtexparser'
    ],
    entry_points={
        'console_scripts': [
            'add_pinyin_key = add_pinyin_key.__main__:main',
        ],
    },
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/Yao1993/add-pinyin-key'
)