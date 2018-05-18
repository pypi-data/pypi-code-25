from setuptools import setup

setup(
    name='termstree',
    description='Library for parsing terms tree from indented text file and searching texts for the tree terms',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=['termstree'],
    install_requires=['pyahocorasick'],
    python_requires='>=3',
    url='https://github.com/gruzovator/termstree',
    license='MIT',
    author='gruzovator',
    author_email='gruzovator@gmail.com',
    keywords='labeling, classification, search, NLP'
)