from setuptools import setup, find_packages

setup(
    name='rovcontrol',
    version='0.2.6',
    author='Aled Cuda',
    author_email='aledvirgil@gmail.com',
    url='https://github.com/ld-cd/rovcontrol/',
    packages=find_packages(),
    install_requires=['websockets', 'RPi.GPIO', 'adafruit-pca9685',],
    license='MIT',
    long_description="I'll document it eventually...",
)
