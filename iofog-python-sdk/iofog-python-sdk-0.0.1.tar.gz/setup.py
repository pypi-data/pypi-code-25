from distutils.core import setup

setup(
    name='iofog-python-sdk',
    version='0.0.1',
    packages=['iofog_python_sdk'],
    url='http://iofog.org',
    license='EPL-2.0',
    author='Eclipse ioFog',
    author_email='edgemaster@iofog.org',
    description='Native python SDK for Eclipse ioFog development.',
    requires=['ws4py'],
    keywords='iofog, IoT, Eclipse, fog, edgeworx',
)
