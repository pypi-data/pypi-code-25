from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='markdown_to_mongodb',
    version='0.1.2',
    packages=['markdown_to_mongodb'],
    url='https://github.com/ryanniebling/markdown_to_mongodb',
    license='MIT',
    author='Ryan Niebling',
    author_email='nieblingr1@nku.edu',
    description=readme(),
    longdescription='README.rst',
    install_requires=['pymongo']
)
