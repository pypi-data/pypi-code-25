from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

setup(
    name='lynkz',
    version='1.0',
    description='Unofficial Python wrapper for the lynkz.me API',
    long_description=long_description,
    url='https://github.com/Ewpratten/lynkz',
    author='Evan Pratten',
    author_email='ewpratten@gmail.com',
    license='MIT',
    packages=['lynkz'],
    install_requires=['requests', 'lxml'],
    zip_safe=False)
