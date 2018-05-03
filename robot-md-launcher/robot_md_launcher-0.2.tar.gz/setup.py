from distutils.core import setup

setup(
    name='robot_md_launcher',
    packages=['robot_md_launcher'],  # this must be the same as the name above
    version='0.2',
    description='A random test lib',
    author='youwi',
    author_email='youwi@github.com',
    url='https://github.com/youwi/robot-md-launcher',  # use the URL to the github repo
    download_url='https://github.com/peterldowns/mypackage/archive/0.1.tar.gz',  # I'll explain this in a second
    keywords=['testing', 'logging', 'example'],  # arbitrary keywords
    classifiers=[],
    entry_points={
        'console_scripts': [
            'robot-md-launcher=robot_md_launcher:main',
        ],
    },
)
