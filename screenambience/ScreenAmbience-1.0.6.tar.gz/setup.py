from setuptools import setup

setup (
    name = 'ScreenAmbience',
    version = '1.0.6',
    description = 'Matches zones on a LIFX-Z strip to the colors on your screen.',
    url = 'https://github.com/EdwinP7/ScreenAmbience',
    author = 'Edwin Perea',
    license = 'MIT',
    packages=['ScreenAmbience'],
    install_requires=['pillow', 'bitstruct'],
    python_requires='>=3',
)
