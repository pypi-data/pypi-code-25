from setuptools import setup, find_packages

setup(
    name='wagtailbookmarklet',
    version=0.1,
    description="Gives Wagtail editors an edit this page' bookmarklet",
    long_description='See https://github.com/torchbox/wagtail-bookmarklet for details',
    url='https://github.com/torchbox/wagtail-bookmarklet',
    author='Tom Dyson',
    author_email='tom+wagtailbookmarklet@torchbox.com',
    license='MIT',
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Topic :: Internet :: WWW/HTTP',
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='development',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "wagtail>=1.12"
    ],
)
