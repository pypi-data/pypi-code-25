import os
import json
import csv
from pathlib import Path

def ensure_dir(directory):
  if not os.path.exists(directory):
    try:
      os.makedirs(directory)
    except OSError as e:
      if e.errno != os.errno.EEXIST:
        raise

def import_json(filename):
  with open(filename) as file:
    return json.load(file)

def export_json(filename, data):
  directory = '/'.join(filename.split('/')[:-1])
  ensure_dir(directory)
  with open(filename, 'w') as file:
    json.dump(data, file)

def import_csv_as_dict_array(filename, delimiter=','):
  with open(filename) as file:
    reader = csv.DictReader(file, delimiter=delimiter, skipinitialspace=True)
    return [{k: v for k, v in row.items()} for row in reader]

def export_csv_from_dict_array(filename, data):
  directory = '/'.join(filename.split('/')[:-1])
  ensure_dir(directory)
  keys = data[0].keys()
  with open(filename, 'w') as file:
    dict_writer = csv.DictWriter(file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)

def find_parent_dir_containing(path, target_name):
  p = Path(path).absolute()
  path_names = [x.name for x in p.iterdir()]
  if target_name in path_names:
    return str(p)
  if str(p) == '/':
    return None
  return find_parent_dir_containing(p.parent, target_name)
