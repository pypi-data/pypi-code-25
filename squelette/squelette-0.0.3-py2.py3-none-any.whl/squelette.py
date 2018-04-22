import sys
import os 
import datetime
import shutil
from pprint import pformat

data_d = os.path.join(os.path.dirname(__file__), 'data')
year = datetime.datetime.now().year

def hello ():
  print('Welcome to squelette')
  print('Data directory is %s' % (data_d))

def main ():
  print('Skeletor main')

def pmsg (m):
  print(m, file=sys.stderr)

def ppmsg (m):
  pmsg(pformat(m))

def perror (m):
  pmsg('ERROR %s' % (m))

def slurp_and_format (directory, filename, mapping):
  path = os.path.join(directory, filename)
  with open(path, 'r') as f:
    s = f.read()
  return s % mapping

def write_string (s, directory, filename):
  path = os.path.join(directory, filename)
  with open(path, 'w') as f:
    f.write(s)

def check_and_make_output_d (directory):
  if os.path.exists(directory):
    perror('%s already exists' % (directory))
    raise SystemExit(1)
  os.mkdir(directory)

def python (mapping):
  # name and description are required
  mapping.setdefault('url', '')
  mapping.setdefault('author', '')
  mapping.setdefault('author_email', '')
  mapping.setdefault('license', 'MIT')
  mapping.setdefault('year', year)
  ppmsg(mapping)

  input_d = os.path.join(data_d, 'python')
  input_module_d = os.path.join(input_d, 'template')
  input_tests_d = os.path.join(input_d, 'tests')
  input_zero_d = os.path.join(input_d, '0')
  input_bin_d = os.path.join(input_d, 'bin')

  output_d = mapping['name']
  output_module_d = os.path.join(mapping['name'], mapping['name'])
  output_tests_d = os.path.join(mapping['name'], 'tests')
  output_zero_d = os.path.join(mapping['name'], '0')
  output_bin_d = os.path.join(mapping['name'], 'bin')

  check_and_make_output_d(output_d)
  check_and_make_output_d(output_module_d)
  check_and_make_output_d(output_tests_d)
  check_and_make_output_d(output_bin_d)

  # This will fail if output_zero_d exists, but note that the parent 
  # directory output_d was already checked above
  shutil.copytree(input_zero_d, output_zero_d)

  filenames = ['LICENSE.txt', 'MANIFEST.in', 'README.rst', 'requirements.txt',
      'setup.cfg', 'setup.py', 'tox.ini', '.gitignore']
  for filename in filenames:
    s = slurp_and_format(input_d, filename, mapping)
    write_string(s, output_d, filename)

  filename = '__init__.py'
  s = slurp_and_format(input_module_d, filename, mapping)
  write_string(s, output_module_d, filename)
  filename = 'template.py'
  s = slurp_and_format(input_module_d, filename, mapping)
  filename = '%(name)s.py' % (mapping)
  write_string(s, output_module_d, filename)

  filename = 'test_template.py'
  s = slurp_and_format(input_tests_d, filename, mapping)
  filename = 'test_%(name)s.py' % (mapping)
  write_string(s, output_tests_d, filename)

  filename = 'hello-template'
  s = slurp_and_format(input_bin_d, filename, mapping)
  filename = 'hello-%(name)s' % (mapping)
  write_string(s, output_bin_d, filename)








