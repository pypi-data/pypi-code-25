from setuptools import setup

setup(name='kunci',
    entry_points={
        'console_scripts': [
            'kunci = kunci.kunci:run',
        ],
    },
    version='0.1',
    description='Random password generator - To prevent annoying password restriction',
    url='http://github.com/rustyworks/kunci',
    author='rustyworks',
    author_email='tristanto.kurniawan@gmail.com',
    license='MIT',
    packages=['kunci'],
    zip_safe=False)
