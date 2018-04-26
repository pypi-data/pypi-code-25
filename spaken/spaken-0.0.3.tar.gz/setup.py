from setuptools import setup


with open('README.rst', 'r') as fh:
    description = '\n'.join(fh.readlines())


setup(
    name='spaken',
    version='0.0.3',
    description=description,
    url='https://github.com/labd/spaken',
    author="Michael van Tellingen",
    author_email="michaelvantellingen@gmail.com",
    install_requires=[
        'boto3',
        'click',
        'pip>=10.0',
    ],
    py_modules=['spaken'],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'console_scripts': {
            'spaken = spaken:main'
        }
    },
    zip_safe=False,
)
