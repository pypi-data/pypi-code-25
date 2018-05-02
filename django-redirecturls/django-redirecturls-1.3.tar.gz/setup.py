from distutils.core import setup

setup(
    name='django-redirecturls',
    packages=['shorturls'],
    version='1.3',
    description='URL redirection',
    author='Alex Nordlund',
    author_email='deep.alexander@gmail.com',
    url="https://github.com/deepy/django-redirecturls",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers", ],
    requires=['django']
)
