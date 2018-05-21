from setuptools import setup

setup(name='sshuserclient',
      packages=['sshuserclient'],
      version='0.1',
      description='An SSHClient which honors ssh_config '
                  'and supports proxyjumping',
      author='Christophe Siraut',
      author_email='d@tobald.eu.org',
      url = 'https://github.com/tobald/sshuserclient',
      license='GPL-3+',
      install_requires=[
                    'paramiko',
                ],
      zip_safe=False)
