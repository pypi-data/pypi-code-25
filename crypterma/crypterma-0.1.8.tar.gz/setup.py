from setuptools import setup

setup(
    name='crypterma',
    version='0.1.8',
    author='George Gabolaev',
    author_email='gabolaev98@gmail.com',
    url='https://github.com/gabolaev/crypterma',
    license='MIT',
    python_requires='>=3.6',
    description='ASCII-chart version of how Bitcoin grows',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    packages=['crypterma','crypterma.configs'],
    install_requires=[
        'termcolor',
        'requests'
        ],
    entry_points={
        'console_scripts': [
            'crypterma = crypterma.__main__:main'
            ]
        },
    )
