from distutils.core import setup

setup(
    name='PhotoRename',
    version='1.0.0',
    author="Jordan Dunn",
    author_email="me@jordan-dunn.com",
    url="https://github.com/JorDunn/photorename",
    packages=['photorename', ],
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=['argparse', 'hashlib']
)
