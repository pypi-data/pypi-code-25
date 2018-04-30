import os
import glob
import setuptools

path = os.path.join(os.path.dirname(__file__), 'src/snore/version.py')
with open(path, 'r') as f:
    exec(f.read())

setuptools.setup(
    name='snore',
    version=__version__,
    description='A small library for building better RESTful APIs.',
    author='Chris Timperley',
    author_email='christimperley@googlemail.com',
    url='https://github.com/ChrisTimperley/snore',
    license='mit',
    python_requires='>=3.5',
    install_requires=[
        'requests>=2.0.0',
        'flask>=0.10',
        'Flask-API'
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest'
    ],
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[
        splitext(basename(path))[0] for path in glob.glob('src/*.py')
    ],
    test_suite = 'tests'
)
