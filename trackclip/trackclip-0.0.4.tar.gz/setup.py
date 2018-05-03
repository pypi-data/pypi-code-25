from setuptools import setup, find_packages

setup(
    name='trackclip',
    version='0.0.4',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    url='https://github.com/protecto/trackclip',
    license='MIT License',
    author='protecto',
    description='Annotate videos by adding an automatically moving frame with a label.',
    install_requires=[
        'numpy>=1.14.3',
        'opencv-contrib-python<=3.4.0.12'
    ]
)
