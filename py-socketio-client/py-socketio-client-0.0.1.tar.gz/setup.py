import io
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


HERE = dirname(abspath(__file__))
LOAD_TEXT = lambda name: io.open(join(HERE, name), encoding='UTF-8').read()
DESCRIPTION = '\n\n'.join(LOAD_TEXT(_) for _ in [
    'README.rst',
    'CHANGES.rst',
])
setup(
    name='py-socketio-client',
    version='0.0.1',
    description='A socket.io client library',
    long_description=DESCRIPTION,
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
    ],
    keywords='socket.io node.js',
    author='Roy Hyunjin Han, Halil Ozercan',
    author_email='halilozercan@gmail.com',
    url='https://github.com/halilozercan/py-socketio-client',
    install_requires=[
        'requests>=2.7.0',
        'six',
        'websocket-client',
        'invisibleroads-macros'
    ],
    tests_require=[
        'nose',
        'coverage',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False)
