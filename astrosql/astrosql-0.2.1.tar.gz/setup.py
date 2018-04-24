from setuptools import setup, find_packages
from pathlib import Path

setup(name='astrosql',
      version='0.2.1',
      description='Simple API to access to existing astronomical MySQL database',
      url='https://github.com/ketozhang/astroSQL',
      author='Keto Zhang, Weikang Zheng',
      author_email='keto.zhang@gmail.com',
      packages=['astrosql'],
      # data_files=[
      #       ('astrosql/', ['astrosql/config.yml'])
      # ],
      install_requires=['peewee', 'termcolor', 'pymysql', 'astropy', 'numpy', 'pandas'],
      include_package_data=True,
      zip_safe=False)

config_file = (Path(__file__).parent/'astrosql'/'config.yml').resolve()
(Path.home()/'.astrosql').mkdir(exist_ok = True)
if not (Path.home()/'.astrosql'/'config.yml').exists():
      config_file.rename(Path.home()/'.astrosql'/'config.yml')
