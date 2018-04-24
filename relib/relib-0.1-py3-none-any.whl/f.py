# f for functional

from collections import Counter
from datetime import timedelta

def distinct(items):
  return list(set(items))

def get_num_args(fn):
  try:
    return fn.__code__.co_argcount
  except:
    return 1

def map(items, fn):
  if get_num_args(fn) == 1:
    return [fn(x) for x in items]
  return [fn(items[i], i) for i in range(len(items))]

def filter(items, fn):
  return [x for x in items if fn(x)]

def flatten(l):
  return [item for sublist in l for item in sublist]

def flat_map(items, fn):
  return flatten(map(items, fn))

def reduce(items, reducer, state):
  for item in items:
    state = reducer(state, item)
  return state

def find(items, fn):
  for item in items:
    if fn(item):
      return item

def find_index(items, fn):
  for i in range(len(items)):
    if fn(items[i]):
      return i

def group(items, fn):
  data_by_key = {}
  for item in items:
    key = fn(item)
    if key not in data_by_key:
      data_by_key[key] = []
    data_by_key[key].append(item)
  return data_by_key

def dict_zip(des):
  keys = list(des.keys())
  length = len(des[keys[0]])

  return [
    {
      key: des[key][i]
      for key in keys
    }
    for i in range(length)
  ]

def dict_from(keys, values):
  return {
    keys[i]: values[i]
    for i in range(len(keys))
  }

def make_combinations_by_dict(des, keys=None, pairs=[]):
  keys = sorted(des.keys()) if keys == None else keys
  if len(keys) == 0:
    return [dict(pairs)]
  key = keys[0]
  remaining_keys = keys[1:]
  new_pairs = [(key, val) for val in des[key]]
  return flatten(
    [make_combinations_by_dict(des, remaining_keys, [pair] + pairs) for pair in new_pairs]
  )

def foreach(items, fn):
  single_argument = get_num_args(fn) == 1
  for i in range(len(items)):
    if single_argument:
      fn(items[i])
    else:
      fn(items[i], i)

def merge_dicts(dicts):
  result = {}
  for dictionary in dicts:
    result.update(dictionary)
  return result

def make_date_range(start_date, end_date):
  num_days = (end_date - start_date).days
  date_range = [start_date + timedelta(days=i) for i in range(num_days)]
  return date_range
