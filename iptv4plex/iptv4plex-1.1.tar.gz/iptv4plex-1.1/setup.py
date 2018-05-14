from setuptools import setup
from setuptools.command.install import install
import os, platform



class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        usr = os.path.expanduser("~")
        if not os.path.isdir(os.path.join(usr, 'iptv4plex')):
            os.mkdir(os.path.join(usr, 'iptv4plex'))
        with open(os.path.join(usr, 'iptv4plex', 'iptv4plex.py'), "wb") as file:
            # get request
            from requests import get
            response = get("https://raw.githubusercontent.com/vorghahn/iptv4plex/master/iptv4plex.py")
            # write to file
            file.write(response.content)
        with open(os.path.join(usr, 'iptv4plex', 'README.md'), "wb") as file:
            # get request
            response = get("https://raw.githubusercontent.com/vorghahn/iptv4plex/master/README.md")
            # write to file
            file.write(response.content)
        if platform.system() == 'Linux':
            try:
                os.system("sudo apt-get install python3-tk")
                latestfile = "https://raw.githubusercontent.com/vorghahn/iptv4plex/master/Linux/iptv4plex"
                with open(os.path.join(usr, 'iptv4plex', 'iptv4plex.py'), "wb") as file:
                    # get request
                    response = get(latestfile)
                    # write to file
                    file.write(response.content)
            except:
                print("No linux EXE")
        elif platform.system() == 'Windows':
            try:
                latestfile = "https://raw.githubusercontent.com/vorghahn/iptv4plex/master/Windows/iptv4plex.exe"
                with open(os.path.join(usr, 'iptv4plex', 'iptv4plex.exe'), "wb") as file:
                    # get request
                    response = get(latestfile)
                    # write to file
                    file.write(response.content)
            except:
                print("No windows EXE")
        elif platform.system() == 'Darwin':
            try:
                latestfile = "https://raw.githubusercontent.com/vorghahn/iptv4plex/master/Macintosh/iptv4plex"
                with open(os.path.join(usr, 'iptv4plex', 'iptv4plex.py'), "wb") as file:
                    # get request
                    response = get(latestfile)
                    # write to file
                    file.write(response.content)
            except:
                print("No mac EXE")


setup(
  name = 'iptv4plex',
  version = '1.1',
  cmdclass = {'install': PostInstallCommand},
  description = 'm3u8 proxy 4 plex',
  python_requires = '>=3.5',
  install_requires=[
          'requests',
          'flask'
  ]
)