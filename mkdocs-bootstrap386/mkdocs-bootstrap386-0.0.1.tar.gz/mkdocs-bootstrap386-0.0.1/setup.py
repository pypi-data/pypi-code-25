from setuptools import setup, find_packages

VERSION = '0.0.1'


setup(
    name="mkdocs-bootstrap386",
    version=VERSION,
    url='https://github.com/lramage94/mkdocs-bootstrap386',
    license='BSD',
    description='Minimal theme for MkDocs',
    author='Lucas Ramage',
    author_email='ramage.lucas@openmailbox.org',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.themes': [
            'bootstrap386 = mkdocs_bootstrap386',
        ]
    },
    zip_safe=False
)
