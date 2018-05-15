from setuptools import setup, find_packages


VERSION = "0.0.2"

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name="pyninjas-blog",
    version=VERSION,
    description="Simple Blog Application for Django",
    long_description=readme,
    keywords="blog, django, pyninjas, simple",
    url="https://github.com/pyninjas/pyninjas-blog",
    author="Emin Mastizada",
    author_email="emin@linux.com",
    license="MIT",
    packages=find_packages(),
    package_data={
        "pyninjas.blog": [
            "templates/blog/*.html",
            "static/blog/blog.css"
        ]
    },
    install_requires=[
        "Django>=1.11",
        "Pillow>=3.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
    ],
    project_urls={
        "Bug Reports": "https://github.com/pyninjas/pyninjas-blog/issues",
        "Source": "https://github.com/pyninjas/pyninjas-blog",
        "Say Thanks!": "https://saythanks.io/to/mastizada",
    },
    zip_safe=False
)
