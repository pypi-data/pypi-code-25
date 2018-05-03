from setuptools import setup

setup(
    name='pyRecoverName',
    version='0.1.0',
    author='宋伟(songwei)',
    author_email='songwei@songwei.io',
    description='A practical program designed for fixing the filename misencoded.',
    long_description='',
    url='https://github.com/xdusongwei/pyRecoverName',
    packages=['pyRecoverName', ],
    ext_modules=[],
    license='MIT',
    entry_points = {
        'console_scripts': ['pyRecoverName=pyRecoverName:main'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
    ],
    install_requires=["argparse", "colorama"],
)
