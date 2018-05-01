from setuptools import setup

setup(name='jo_story',
      version='0.1',
      description='story about jo',
      author='John Lhota',
      author_email='johnlhota@example.com',
      license='MIT',
      packages=['jo_story'],
      install_requires=[
          'opencv-python',
      ],
      include_package_data=True,
      zip_safe=False)