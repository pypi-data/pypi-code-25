from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='sshJUNOS',
      version='2.0',
      description='ssh module for Juniper OS',
      long_description=readme(),
      url='https://github.com/FedericoOlivieri/networkAutomation/blob/master/python/modules/sshJUNOS/sshJUNOS/__init__.py',
      author='Federico Olivieri',
      author_email='lvrfrc87@gmail.com',
      license='MIT',
      packages=['sshJUNOS'],
      install_requires=['netmiko',],
      zip_safe=False)
