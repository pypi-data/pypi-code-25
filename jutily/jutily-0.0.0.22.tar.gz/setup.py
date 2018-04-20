from setuptools import setup


setup(
    name='jutily',
    version='0.0.0.22',
    description='',
    url='https://github.com/the16thpythonist/ScopusWp',
    author='Jonas Teufel',
    author_email='jonseb1998@gmail.com',
    license='MIT',
    packages=['jutil', 'jutil/database'],
    include_package_data=True,
    install_requires=[
        'sqlalchemy>=1.2',
        'jinja2>=2.10',
        'deprecated'
    ],
    python_requires='>=3, <4'
)
