from setuptools import setup

setup(name='bimeta',
    version='1.3.1',
    python_requires='>3.5.2',
    description='bimeta client',
    url='https://github.com/trbpnd/bimeta',
    author='tr-',
    author_email='rahmanovic@gmail.com',
    license='MIT',
    packages=['bimeta'],
    entry_points = {
        'console_scripts': ['bimeta=bimeta.bimeta:bimetamain'],
    },
    install_requires=[
            'termcolor',
            'pyaml',
            'requests'
          ],
    zip_safe=False)

