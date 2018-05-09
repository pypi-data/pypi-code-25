from setuptools import setup, find_packages


setup(
    name='panoramik-slogging-flask',
    version='0.2.2',
    description='Panoramik logging library (for Flask-based web apps)',
    url='https://gitlab.panoramik.ru/leenr/logging-python',
    author='leenr',
    author_email='i@leenr.ru',
    license='Proprietary',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, <4',
    install_requires=[
        'blinker>=1.4.0',
        'six>=1.7',
        'flask>=0.9',
        'fluent-logger>=0.9.0',
        'qualname>=0.1.0',
        'uwsgidecorators>=1.1.0'
    ],
    packages=find_packages(),
    zip_safe=True
)
