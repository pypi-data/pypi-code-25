from setuptools import setup


setup(
    name='pubcontrol_core',
    version='0.0.0.2',
    description='A tool for a wordpress server which will automatically post science publications from scopus database',
    url='https://github.com/the16thpythonist/ScopusWp',
    author='Jonas Teufel',
    author_email='jonseb1998@gmail.com',
    license='MIT',
    packages=['pubcontrol'],
    include_package_data=True,
    install_requires=[
        'requests>=2.0',
        'mysqlclient>=1.2',
        'unidecode>=0.4',
        'tabulate>=0.8',
        'python-wordpress-xmlrpc>=2.3',
        'jinja2>=2.10',
        'sqlalchemy>=1.2',
        'memory_profiler',
        'jutily',
        'pluggy'
    ],
    python_requires='>=3, <4',
    package_data={
        '': []
    },
)
