import tempfile
import os
import shutil
from io import BytesIO
from copy import copy
from subprocess import call
from pathlib import Path
from random import random
from functools import partial

def ensure_list(val):
  if isinstance(val, (tuple, list)):
    return list(val)
  else:
    return [val]

def get_tmp_path():
  tmp_dir = tempfile.gettempdir()
  destination = 'tmp' + str(random())[2:]
  return tmp_dir + '/' + destination

def get_tmp_directory():
  dir_path = get_tmp_path() + '/'
  os.makedirs(dir_path)
  return dir_path

class BinaryWrapper:
  def __init__(self):
    self.tmp_dir = get_tmp_directory()

  def __enter__(self):
    return self

  def __exit__(self, *_):
    p = Path(self.tmp_dir)
    file_names = [x.name for x in p.iterdir()]

    def to_bytes(path):
      with open(path, 'rb') as file:
        return BytesIO(file.read())

    self.byte_map = {
      file_name: to_bytes(self.tmp_dir + '/' + file_name)
      for file_name in file_names
    }

    shutil.rmtree(self.tmp_dir)

  def unwrap(self):
    return BinaryUnwrapper(self)

class BinaryUnwrapper:
  def __init__(self, binary_wrapper):
    self.binary_wrapper = binary_wrapper
    self.tmp_dir = get_tmp_directory()

  def __enter__(self):
    byte_map = self.binary_wrapper.byte_map
    for file_name in byte_map:
      path = self.tmp_dir + file_name
      with open(path, 'wb') as file:
        data = copy(byte_map[file_name]).read()
        file.write(data)
    return self.tmp_dir

  def __exit__(self, *_):
    try:
      shutil.rmtree(self.tmp_dir)
    except FileNotFoundError:
      pass

class TerminalPlot():
  file_name = 'plot.png'

  def __init__(self, plt):
    with BinaryWrapper() as binary_wrapper:
      plt.savefig(binary_wrapper.tmp_dir + self.file_name)
      self.binary_wrapper = binary_wrapper

  def show(self):
    with self.binary_wrapper.unwrap() as tmp_dir:
      call(['imgcat', tmp_dir + self.file_name])

  def savefig(self, path):
    with self.binary_wrapper.unwrap() as tmp_dir:
      os.rename(tmp_dir + 'plot.png', path)

class PickleableKerasModel():
  file_name = 'model.h5'

  def __init__(self, model):
    with BinaryWrapper() as binary_wrapper:
      model.save(binary_wrapper.tmp_dir + self.file_name)
      self.binary_wrapper = binary_wrapper

  def unwrap(self):
    from keras.models import load_model
    with self.binary_wrapper.unwrap() as tmp_dir:
      return load_model(tmp_dir + self.file_name)

class PickleableTf:
  def __init__(self, get_model_funcs, *args, **kwargs):
    from checkpointer import get_function_hash

    model_funcs_names = kwargs.get('model_funcs_names', None)
    binary_wrapper = kwargs.get('binary_wrapper', None)

    if 'model_funcs_names' in kwargs:
      del kwargs['model_funcs_names']
      del kwargs['binary_wrapper']

    if model_funcs_names == None:
      import tensorflow as tf

      with tf.Graph().as_default():
        model_funcs = ensure_list(get_model_funcs(*args, **kwargs))
        model_funcs_names = [func.__name__ for func in model_funcs]

    self.args = args
    self.kwargs = kwargs
    self.model_funcs_names = model_funcs_names
    self.get_model_funcs = get_model_funcs
    self.get_model_funcs_hash = get_function_hash(get_model_funcs)
    self.binary_wrapper = binary_wrapper

    for func_name in model_funcs_names:
      compute = partial(self._compute, func_name)
      setattr(self, func_name, compute)

  def _compute(self, func_name, *args, **kwargs):
    import tensorflow as tf

    with tf.Graph().as_default():
      model_funcs = {
        func.__name__: func
        for func in ensure_list(self.get_model_funcs(*self.args, **self.kwargs))
      }

      ckpt_file_name = 'tf.ckpt'
      saver = tf.train.Saver()

      with tf.Session() as sess:
        binary_wrapper = self.binary_wrapper

        def save():
          nonlocal binary_wrapper
          with BinaryWrapper() as binary_wrapper:
            saver.save(sess, binary_wrapper.tmp_dir + ckpt_file_name)

        if self.binary_wrapper:
          with self.binary_wrapper.unwrap() as tmp_dir:
            saver.restore(sess, tmp_dir + ckpt_file_name)
        else:
          init_op = tf.global_variables_initializer()
          sess.run(init_op)

        result = model_funcs[func_name](sess, save, *args, **kwargs)
        model = PickleableTf(
          self.get_model_funcs,
          *self.args,
          **self.kwargs,
          model_funcs_names=self.model_funcs_names,
          binary_wrapper=binary_wrapper
        )
        return model, result
