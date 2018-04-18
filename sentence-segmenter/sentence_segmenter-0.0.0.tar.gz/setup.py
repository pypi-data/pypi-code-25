from setuptools import setup, find_packages

version = "0.0.0"
name = "sentence_segmenter"

setup(
    name=name,
    version=version,
    description="Sentence Segmentation with Cython",
    author="Brian Lester",
    author_email="blester125@gmail.com",
    url=f"https://github.com/blester125/{name}",
    download_url=f"https://github.com/blester125/{name}/archive/{version}.tar.gz",
    license="MIT",
    packages=find_packages(),
)
