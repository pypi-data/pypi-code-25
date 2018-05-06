from io import open
import sys

from setuptools import (
    find_packages,
    setup,
)

setup(
    name="xpybutil",
    maintainer="Fenner Macrae",
    maintainer_email="fmacrae.dev@gmail.com",
    version="0.0.4",
    license="WTFPL",
    description="An incomplete xcb-util port plus some extras",
    install_requires=['xcffib'],
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    url="http://github.com/fennerm/xpybutil",
    packages=find_packages(),
    keywords='xorg X xcb xpyb xcffib',
    data_files=[('share/doc/xpybutil', ['README.md', 'LICENSE'])]
)
