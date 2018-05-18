import setuptools


try:
    with open("README.rst") as f:
        long_description = f.read()
except:
    long_description = None

setuptools.setup(
    name="mk60",
    version="0.2a2",
    description="Utility assisting in creation of D3-28 tapes",
    url="https://github.com/xoiss/mk60",
    author="Alexander A. Strelets",
    author_email="StreletsAA@gmail.com",
    license="Public Domain",
    download_url="https://github.com/xoiss/mk60",
    long_description=long_description,
    platforms=['Linux', 'Windows', 'macOS'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis',
    ],
    packages=["mk60"],
    entry_points={
        'console_scripts': [
            'mk60 = mk60.app:main',
        ],
    },
)
