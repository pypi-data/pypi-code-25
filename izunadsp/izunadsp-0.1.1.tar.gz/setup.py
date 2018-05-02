# External Libraries
from setuptools import setup

# IzunaDSP
from izunadsp import misc

with open("README.rst") as file:
    README = file.read()

with open("requirements.txt") as file:
    REQUIREMENTS = file.readlines()

if __name__ == '__main__':
    setup(
        name="izunadsp",
        author="izunadevs",
        author_email="izunadevs@martmists.com",
        maintainer="martmists",
        maintainer_email="mail@martmists.com",
        license="MIT",
        zip_safe=False,
        version=misc.__version__,
        description=misc.description,
        long_description=README,
        url="https://github.com/IzunaDevs/IzunaDSP",
        packages=['izunadsp'],
        install_requires=REQUIREMENTS,
        keywords=["audio", "audio processing", "DSP"],
        classifiers=[
            "Development Status :: 2 - Pre-Alpha", "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Topic :: Multimedia :: Sound/Audio",
            "Topic :: Multimedia :: Sound/Audio :: Analysis",
            "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
            "Topic :: Software Development :: Libraries :: Python Modules"
        ],
        python_requires=">=3.0")
