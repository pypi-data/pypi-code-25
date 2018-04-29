from setuptools import find_packages, setup


with open('README.rst', 'r') as fh:
    description = '\n'.join(fh.readlines())


setup(
    name='spaken',
    version='0.0.8',
    description=description,
    url='https://github.com/labd/spaken',
    author="Michael van Tellingen",
    author_email="michaelvantellingen@gmail.com",
    install_requires=[
        'boto3',
        'click>=6.7',
        'pip>=10.0',
        'packaging>=17.0',
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'console_scripts': {
            'spaken = spaken.main:main'
        }
    },
    zip_safe=False,
)
