#!/usr/bin/env python3
"""pwclip packaging information"""
from os.path import join as pjoin

name = distname = modname = 'pwclip'
numversion = (1, 3, 1)
version = '.'.join([str(num) for num in numversion])
provides = ['pwcli', 'pwclip', 'ykclip']
install_requires = [
    'argcomplete', 'netaddr', 'paramiko', 'psutil',
    'pyusb', 'python-gnupg', 'python-yubico', 'PyYAML', 'wget']
license = 'GPL'
description = "gui to temporarily save passwords to system-clipboard"
mailinglist = ""
author = 'Leon Pelzer'
author_email = 'mail@leonpelzer.de'
download_url = 'https://pypi.python.org/pypi/pwclip/%s#downloads'%version
classifiers = ['Environment :: Console',
               'Environment :: MacOS X',
               'Environment :: Win32 (MS Windows)',
               'Environment :: X11 Applications',
               'Intended Audience :: Developers',
               'Intended Audience :: End Users/Desktop',
               'Intended Audience :: System Administrators',
               'Intended Audience :: Information Technology',
               'License :: OSI Approved :: GNU General Public License (GPL)',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 3',
               'Topic :: Security',
               'Topic :: Utilities',
               'Topic :: Desktop Environment',
               'Topic :: System :: Systems Administration']
include_package_data = True
try:
	with open('pwclip/docs/CHANGELOG.rst', 'r') as cfh:
		changelog = '\n\n\n'.join(cfh.read().split('\n\n\n')[:4])
except OSError:
	changelog = ''
try:
	with open('pwclip/docs/README.rst', 'r') as rfh:
		readme = rfh.read().format(ChangeLog=changelog)
except OSError:
	readme = ''
long_description = (readme)
entry_points = {
    'gui_scripts': ['pwclip = pwclip.__init__:pwclip',
                    'ykclip = pwclip.__init__:ykclip'],
    'console_scripts': ['pwcli = pwclip.__init__:pwcli']}
package_data = {
    '': ['pwclip/docs/*.rst']}
data_files=[
    ('share/man/man1', ['pwclip/docs/pwclip.1']),
    ('share/pwclip', [
        'pwclip/example/ca.crt', 'pwclip/example/commands.lst',
        'pwclip/example/ssl.crt', 'pwclip/example/ssl.key',
        'pwclip/example/example_passwords.yaml'])]
