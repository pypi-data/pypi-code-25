from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='sshEOS',
      version='2.0',
      description='python3 ssh module for Arista EOS',
      long_description=readme(),
      url='https://github.com/FedericoOlivieri/networkAutomation/blob/master/python/modules/sshEOS/sshEOS/__init__.py',
      author='Federico Olivieri',
      author_email='lvrfrc87@gmail.com',
      license='MIT',
      packages=['sshEOS'],
      install_requires=['netmiko',],
      zip_safe=False)
