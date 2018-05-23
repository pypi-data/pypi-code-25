from setuptools import setup, find_packages


setup(
    name='gatsby-normalizer',
    version='1.0.1',
    description='Normalize Keyword, URL, and etc.',
    long_description=open('README.rst').read(),
    url='https://github.com/Gatsby-Lee/GatsbyPythonNormalizer',
    author='Gatsby Lee',
    author_email='gatsbylee.dev@gmail.com',
    keywords=['gatsby', 'normalizer'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
)
