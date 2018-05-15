from distutils.core import setup

long_description = open('README.rst').read()

setup(
    name='django2-url-robots',
    version='3.0',
    description='Django robots.txt generator',
    long_description=long_description,
    url='https://github.com/maximekl/django2-url-robots',
    author='Maxime Klampas',
    author_email='mklampas@gmail.com',
    license='Python Software Foundation License',
    packages=['django2_url_robots', 'django2_url_robots.tests'],
    package_data={'django2_url_robots': ['templates/*.*']},
    platforms=["any"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Framework :: Django',
        ],
)
