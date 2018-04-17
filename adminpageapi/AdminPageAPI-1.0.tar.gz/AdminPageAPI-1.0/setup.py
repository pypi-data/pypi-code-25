from setuptools import setup, find_packages

setup(
    name='AdminPageAPI',
    version='1.0',
    packages=find_packages('AdminPageAPI', exclude=['test*']),
    url='',
    license='',
    author='seitze2',
    author_email='seitze2@nku.edu',
    description='Admin Page for Wiki System',
    install_requires=[
          'os', 'flask'
      ]
)
