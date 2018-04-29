from setuptools import setup, find_packages
from codecs import open
from os import path
current_dir = path.abspath(path.dirname(__file__))

with open(path.join(current_dir, 'README.md'), encoding='utf-8') as readme:
    long_description = readme.read()

try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {"build_ui": build_ui}
except ImportError:
    cmdclass = {}

try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')
except ImportError:
    convert = None
    print(
        "warning: pypandoc module not found, could not convert Markdown to RST"
    )

    def read_md(f):
        return open(f, 'r').read()

README = path.join(current_dir, 'README.md')

setup(
    name='glMAC',
    version='0.0.7',
    description="Retrieves vendor information from MAC address",
    long_description=read_md(README),
    url='https://git.gallochri.com/gallochri/glMAC',
    author='gallochri',
    author_email='chri@gallochri.com',
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: X11 Applications :: Qt',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: System',
                 'Topic :: System :: Hardware'],
    keywords=['MAC', 'vendor', 'MAC Addresses'],
    packages=find_packages(),
    install_requires=[
        # PyQT5 dependency creates problems in packaging for opensuse
        # 'PyQt5',
        'requests'],
    extras_require={
        'dev': ['pyqt-distutils', 'pypandoc'],
        'test': ['coverage'],
    },
    package_data={'glMAC': ['images/*', 'resources/mainwindow.*']},
    entry_points={
        'console_scripts': [
            'glMAC=glMAC.__main__:main'
        ]
    },


    download_url='https://git.gallochri.com/gallochri/glMAC.git',
    python_requires='>=3.4',
    provides=['glMAC'],
    platforms='any',
    license='GPLv3',
    py_modules=['glMAC', ],
    cmdclass=cmdclass
)
