import tempfile
import os
from random import random

def get_tmp_path():
  tmp_dir = tempfile.gettempdir()
  destination = 'tmp' + str(random())[2:]
  return tmp_dir + '/' + destination

def get_tmp_directory():
  dir_path = get_tmp_path() + '/'
  os.makedirs(dir_path)
  return dir_path
