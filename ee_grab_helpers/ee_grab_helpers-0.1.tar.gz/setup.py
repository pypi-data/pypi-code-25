from setuptools import setup

setup(name='ee_grab_helpers',
      version='0.1',
      description='Helper functions for the Google Earth Engine Python API',
      url='https://github.com/JesJehle/earthEngineGrabR',
      author='Janusch Jehle',
      author_email='JesJehle@gmx.de',
      license='MIT',
      packages=['ee_grab_helpers'],
      install_requires=[
          'google-api-python-client',
          'pyCrypto',
          'earthengine-api',
	  'pandas'],
      zip_safe=False)

