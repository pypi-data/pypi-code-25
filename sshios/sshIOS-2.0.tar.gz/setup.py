from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='sshIOS',
      version='2.0',
      description='ssh module for Cisco IOS',
      long_description=readme(),
      url='https://github.com/FedericoOlivieri/networkAutomation/blob/master/python/modules/sshIOS/sshIOS/__init__.py',
      author='Federico Olivieri',
      author_email='lvrfrc87@gmail.com',
      license='MIT',
      packages=['sshIOS'],
      install_requires=['netmiko',],
      zip_safe=False)
