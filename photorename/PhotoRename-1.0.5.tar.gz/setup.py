from distutils.core import setup

setup(
    name='PhotoRename',
    version='1.0.5',
    author="Jordan Dunn",
    author_email="me@jordan-dunn.com",
    url="https://github.com/JorDunn/photorename",
    packages=['photorename', ],
    license='MIT',
    long_description="A utility to rename photos and give them a more unified filename.",
    entry_points={
        'console_scripts': ['photorename=photorename.command_line:main'],
    }
)
