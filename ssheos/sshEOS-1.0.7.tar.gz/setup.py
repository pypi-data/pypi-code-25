from setuptools import setup

setup(name='sshEOS',
      version='1.0.7',
      description='python3 ssh module for Arista EOS',
      url='https://github.com/FedericoOlivieri/networkAutomation/blob/master/python/modules/python3/sshEOS/sshEOS/__init__.py',
      author='Federico Olivieri',
      author_email='lvrfrc87@gmail.com',
      license='MIT',
      packages=['sshEOS'],
      install_requires=['netmiko',],
      zip_safe=False)
