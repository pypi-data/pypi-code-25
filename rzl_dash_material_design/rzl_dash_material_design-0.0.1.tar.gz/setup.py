from setuptools import setup

exec (open('rzl_dash_material_design/version.py').read())

setup(
    name='rzl_dash_material_design',
    version=__version__,
    author='rzachlamberty',
    packages=['rzl_dash_material_design'],
    include_package_data=True,
    license='MIT',
    description='material design components for dash',
    install_requires=[]
)
