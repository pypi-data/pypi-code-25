from setuptools import setup, find_packages

setup(
    name='rovcontrol',
    version='0.5.4',
    author='Aled Cuda',
    author_email='aledvirgil@gmail.com',
    url='https://github.com/ld-cd/rovcontrol/',
    packages=find_packages(),
    install_requires=['websockets', 'RPi.GPIO', 'adafruit-pca9685', 'adafruit-mcp3008', 'adafruit-gpio',],
    license='MIT',
    long_description="I'll document it eventually...",
)
