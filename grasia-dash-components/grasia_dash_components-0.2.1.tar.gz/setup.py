from setuptools import setup

exec (open('grasia_dash_components/version.py').read())

setup(
    name='grasia_dash_components',
    version=__version__,
    author="Abel 'Akronix' Serrano Juste",
    author_email='akronix5@gmail.com',
    packages=['grasia_dash_components'],
    include_package_data=True,
    license='MIT',
    description='Dash UI component suite',
    install_requires=[]
)
