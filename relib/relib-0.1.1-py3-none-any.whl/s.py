# s for statistics

import numpy as np
from . import f
from collections import Counter
from pprint import pprint

def get_list_of_dominant_values(items, threshold=0.05):
  num_items = len(items)
  freq_by_value = Counter(items)
  distinct_values = sorted(freq_by_value.keys())
  dominant_values = [val for val in distinct_values if freq_by_value[val] / num_items >= threshold]
  return dominant_values, distinct_values

def get_one_hotter_categories(items, by_key, threshold=0):
  values = [item[by_key] for item in items]
  dominant_values, distinct_values = get_list_of_dominant_values(values, threshold)
  exclude_other = len(dominant_values) == len(distinct_values)
  categories = dominant_values if exclude_other else dominant_values + ['_OTHER_']
  return categories

def list_dict_distinct_values(items, threshold=0):
  fields = items[0].keys()
  return {field: get_one_hotter_categories(items, field, threshold) for field in fields}

def create_plain_one_hotter(values):
  normal_map = {}

  def create_normal(value, multiplier):
    if value not in normal_map:
      normal_map[value] = {}
    normal = [multiplier if value == value2 else 0 for value2 in values]
    normal_map[value][multiplier] = normal
    return normal

  def one_hot(_value, multiplier=1):
    value = _value if _value in values else '_OTHER_'
    if value in normal_map and multiplier in normal_map[value]:
      return normal_map[value][multiplier]
    if value not in values:
      raise ValueError('Value <' + str(_value) + '> does not exist')
    else:
      return create_normal(value, multiplier)

  return one_hot

def create_one_hotter(values_by_field):
  fields = sorted(values_by_field.keys())
  one_hot_by_field = {field: create_plain_one_hotter(values_by_field[field]) for field in fields}

  def one_hot(item, multiplier=1):
    x = [one_hot_by_field[field](item[field], multiplier) for field in fields]
    return f.flatten(x)

  return one_hot

class AlmostGodEncoder:
  def __init__(self, matrix):
    self.values_locations = {}
    self.one_hot_map = {}
    sample_row = matrix[0] if matrix else []
    x_range = range(len(sample_row))
    y_range = list(range(len(matrix)))

    for x in x_range:
      values = [matrix[y][x] for y in y_range]
      distinct_ordered_values = sorted(set(values))
      shortened_y_range = range(len(distinct_ordered_values))

      self.one_hot_map[x] = {}

      self.values_locations[x] = {
        distinct_ordered_values[y]: y
        for y in shortened_y_range
      }

  def create_one_hot_by_x(self, x, value):
    index_by_val = self.values_locations[x]
    one_hot_by_val = self.one_hot_map[x]
    value_index = index_by_val[value]
    max_index = len(index_by_val)
    normal = [1 if value_index == i else 0 for i in range(max_index)]
    one_hot_by_val[value] = normal

  def get_one_hot_by_x(self, x, value):
    index_by_val = self.values_locations[x]
    one_hot_by_val = self.one_hot_map[x]

    if value in index_by_val:
      if value not in one_hot_by_val:
        self.create_one_hot_by_x(x, value)
      return one_hot_by_val[value]
    else:
      raise ValueError('Value <' + str(value) + '> does not exist')

  def one_hot(self, matrix):
    sample_row = matrix[0] if matrix else []
    x_range = list(range(len(sample_row)))

    return np.array([
      np.concatenate([self.get_one_hot_by_x(x, row[x]) for x in x_range])
      for row in matrix
    ])

  def label_encode(self, matrix):
    values_locations = self.values_locations
    sample_row = matrix[0] if matrix else []
    x_range = list(range(len(sample_row)))

    return np.array([
      np.array([values_locations[x][row[x]] for x in x_range])
      for row in matrix
    ])

class MinMaxer():
  def __init__(self, x):
    if type(x[0]) == MinMaxer:
      x = np.vstack([[minmaxer.data_min, minmaxer.data_max] for minmaxer in x])
    else:
      x = x.reshape(self.to_target_shape(x.shape))
    self.data_min = np.min(x, axis=0)
    self.data_max = np.max(x, axis=0)
    data_range = self.data_max - self.data_min
    data_range[data_range == 0.0] = 1.0
    self.scale = 1 / data_range
    self.min = -self.data_min * self.scale

  def transform(self, x):
    org_shape = x.shape
    x = x.reshape(self.to_target_shape(org_shape))
    x = x * self.scale + self.min
    return x.reshape(org_shape)

  def inverse_transform(self, x):
    org_shape = x.shape
    x = x.reshape(self.to_target_shape(org_shape))
    x = (x - self.min) / self.scale
    return x.reshape(org_shape)

  def to_target_shape(self, shape):
    if len(shape) == 1:
      return (-1, 1)
    return (-1, shape[-1])

def iterate_grids(make_params, fn):
  initial_params_set = [f.make_combinations_by_dict(param_set) for param_set in make_params]
  initial_params = f.merge_dicts(*[params_set[0] for params_set in initial_params_set])

  def next_iteration(default_params, params_sets, scores_params_list=[]):
    if len(params_sets) == 0:
      return scores_params_list

    uncleared_set = params_sets[0]
    params_list = [{**default_params, **additional_params} for additional_params in uncleared_set]
    scores = [fn(params) for params in params_list]
    new_scores_params_list = f.dict_zip({'score': scores, 'params': params_list})
    scores_params_list = sorted(new_scores_params_list + scores_params_list, key=lambda x: x['score'])
    min_score_index = scores.index(min(scores))
    additional_params = uncleared_set[min_score_index]
    new_default_params = {**default_params, **additional_params}
    return next_iteration(new_default_params, params_sets[1:], scores_params_list)

  return next_iteration(initial_params, initial_params_set)

def get_model(on_params, grid_data, current_data, grids):
  print('Grid searching')

  scores_params_list = iterate_grids(
    grids,
    lambda params: on_params(params, grid_data[0], grid_data[1], grid_data[2], grid_data[3])[1]
  )

  best_params = scores_params_list[0]['params']
  print('Best params:')
  pprint(best_params)

  model = on_params(best_params, current_data[0], current_data[1], current_data[2], current_data[3])[0]
  return model
