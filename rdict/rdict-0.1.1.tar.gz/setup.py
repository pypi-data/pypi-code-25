from setuptools import setup

setup(
    name='rdict',
    version='0.1.1',
    author='songwei',
    author_email='songwei@songwei.io',
    description='A Pythonic tool is used for operating redis commands.',
    long_description='',
    url='https://github.com/xdusongwei/rdict',
    python_requires='>=3',
    packages=['rdict'],
    ext_modules=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=["redis"],
)
