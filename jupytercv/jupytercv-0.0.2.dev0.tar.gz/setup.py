from setuptools import setup, find_packages

setup(
    name='jupytercv',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    version='0.0.2.dev',
    description='Computer vision utils for Jupyter notebook',
    author='Sanghoon Yoon',
    author_email='shygiants@gmail.com',
    url='https://github.com/shygiants/jupytercv',
    keywords=['jupyter', 'notebook'],
    classifiers=[],
    install_requires=[
        'numpy',
        'matplotlib',
        'Pillow'
    ],
)
