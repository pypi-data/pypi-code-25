from setuptools import setup, find_packages

version = "0.0.0"
name = "quick_knn"

setup(
    name=name,
    version=version,
    description="LSH with Cosine distance",
    author="Brian Lester",
    author_email="blester125@gmail.com",
    url=f"https://github.com/blester125/{name}",
    download_url=f"https://github.com/blester125/{name}/archive/{version}.tar.gz",
    license="MIT",
    packages=find_packages(),
    package_data={
        name: [
        ],
    },
    include_package_data=True,
    install_requires=[
    ],
    keywords=['Data Mining']
)
