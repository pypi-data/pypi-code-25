import tempfile
import os
import shutil
from io import BytesIO
from copy import copy
from pathlib import Path
from random import random

def get_tmp_path():
  tmp_dir = tempfile.gettempdir()
  destination = 'tmp' + str(random())[2:]
  return tmp_dir + '/' + destination

def get_tmp_directory():
  dir_path = get_tmp_path() + '/'
  os.makedirs(dir_path)
  return dir_path

class DirectoryBytesIO:
  def __init__(self, cb):
    tmp_directory = get_tmp_directory()
    cb(tmp_directory)
    p = Path(tmp_directory)
    file_names = [x.name for x in p.iterdir()]

    def to_bytes(path):
      with open(path, 'rb') as file:
        return BytesIO(file.read())

    self.byte_map = {
      file_name: to_bytes(tmp_directory + '/' + file_name)
      for file_name in file_names
    }

    shutil.rmtree(tmp_directory)

  def unpack(self, cb):
    tmp_directory = get_tmp_directory()
    for file_name in self.byte_map:
      path = tmp_directory + '/' + file_name
      with open(path, 'wb') as file:
        data = copy(self.byte_map[file_name]).read()
        file.write(data)
    cb(tmp_directory)
    shutil.rmtree(tmp_directory)
