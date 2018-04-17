from setuptools import setup
setup(
    name='Flask-CacheBuster',
    version='1.0.0',
    description='Flask-CacheBuster is a lightweight Flask extension that adds a hash to the URL query parameters of each static file.',
    packages=['flask_cachebuster'],
    long_description=open('README.rst').read(),
    author="Israel Flores",
    author_email="jobs@israelfl.com",
    license='MIT',
    url='https://github.com/israel-fl/Flask-CacheBuster',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging'
    ],
    install_requires=[
        'Flask',
    ],
)
