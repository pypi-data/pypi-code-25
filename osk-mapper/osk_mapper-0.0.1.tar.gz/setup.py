from setuptools import setup

with open('version.txt') as file:
    version = file.read().strip()

setup(name='osk_mapper',
      version=version,
      description='Utility to map coordinates of OSK',
      author='Jonathon Carlyon',
      author_email='JonathonCarlyon@gmail.com',
      url='https://github.com/JonnyFb421/MapleBot',
      install_requires=['pyautogui'],
      extras_require={'dev': ['pytest']},
      packages=['osk_mapper', 'osk_mapper.resources'],
      package_data={'osk_mapper': ['resources/osk/*/*.png']},
      )
