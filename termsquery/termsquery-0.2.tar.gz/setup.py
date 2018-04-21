from setuptools import setup

setup(
    name='termsquery',
    description='Terms boolean expressions to query containers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    py_modules=['termsquery'],
    python_requires='>=3',
    url='https://github.com/gruzovator/termsquery',
    license='MIT',
    author='gruzovator',
    author_email='gruzovator@github.com',
    keywords='boolean expression, logic, expression parser, tagging, tag',
)
