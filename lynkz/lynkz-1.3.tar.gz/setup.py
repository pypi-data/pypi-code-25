from setuptools import setup


setup(
    name='lynkz',
    version='1.3',
    description='Unofficial Python wrapper for the lynkz.me API',
    long_description=open("README.rst").read(),
    url='https://github.com/Ewpratten/lynkz',
    author='Evan Pratten',
    author_email='ewpratten@gmail.com',
    license='MIT',
    packages=['lynkz'],
    install_requires=['requests', 'lxml'],
    zip_safe=False)
