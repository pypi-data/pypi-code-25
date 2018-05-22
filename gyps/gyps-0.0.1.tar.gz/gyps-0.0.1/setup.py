import os.path
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), mode='r', encoding='utf-8') as f:
    readme = f.read()

setuptools.setup(
    name='gyps',
    version='0.0.1',
    description='[WiP; Name Squatting] - Python transcoding tools for geodetic files',
    long_description=readme,
    author='Jean-Charles Lefebvre',
    author_email='polyvertex@gmail.com',
    url='https://github.com/polyvertex/gyps',
    license='MIT',
    keywords=['gps', 'convert', 'gpx', 'kml', 'kmz', 'nmea', 'sbn', 'sbp'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'],

    packages=[],

    python_requires='>=3.6',
    install_requires=[],
    extras_require={})
