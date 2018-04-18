from setuptools import setup, find_packages

version = "0.0.0"

setup(
    name="text_rank",
    version=version,
    description="Text Rank with Cython",
    author="Brian Lester",
    author_email="blester125@gmail.com",
    url="https://github.com/blester125/text_rank",
    download_url=f"https://github.com/blester125/text_rank/archive/{version}.tar.gz",
    license="MIT",
    packages=find_packages(),
)
