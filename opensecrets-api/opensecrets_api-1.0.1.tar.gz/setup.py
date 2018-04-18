from setuptools import setup

setup(name='opensecrets_api',
    version='1.0.1',
    description='API to access the opensecrets.org information',
    url='https://github.com/kartikye/opensecrets_api/',
    author='Kartikye Mittal',
    author_email='kartikye.mittal+opensecrets_api@gmail.com',
    license='MIT',
    packages=['opensecrets_api'],
    zip_safe=False,
    python_requires='>=3',
    install_requires=[
        'requests'
    ])