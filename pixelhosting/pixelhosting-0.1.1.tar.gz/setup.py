from setuptools import setup, find_packages

setup(
    name="pixelhosting",
    version="0.1.1",
    description="Python package for PixelHosting.",
    url="https://github.com/amosbastian/pixelhosting-python-sdk",
    author="Amos Bastian",
    author_email="amosbastian@googlemail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="pixelhosting wehmoen",
    packages=find_packages(),
    install_requires=["requests"],
)
