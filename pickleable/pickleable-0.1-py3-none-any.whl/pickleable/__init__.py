import tempfile
import os
import shutil
from io import BytesIO
from copy import copy
from subprocess import call
from pathlib import Path
from random import random
from functools import partial
from checkpointer import get_function_hash

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

class TerminalPlot():
  def __init__(self, plt):
    tmp_path = get_tmp_path() + '.png'
    plt.savefig(tmp_path)
    with open(tmp_path, 'rb') as file:
      self.wrapped_plot = BytesIO(file.read())
    os.remove(tmp_path)
    plt.close()

  def show(self):
    tmp_path = get_tmp_path() + '.png'
    self.savefig(tmp_path)
    call(['imgcat', tmp_path])
    os.remove(tmp_path)

  def savefig(self, path):
    with open(path, 'wb') as file:
      data = copy(self.wrapped_plot).read()
      file.write(data)

class PickleableKerasModel():
  def __init__(self, model):
    tmp_path = get_tmp_path() + '.h5'
    model.save(tmp_path)
    with open(tmp_path, 'rb') as file:
      self.wrapped_model = BytesIO(file.read())

  def unwrap(self):
    from keras.models import load_model
    tmp_path = get_tmp_path() + '.h5'
    with open(tmp_path, 'wb') as file:
      data = copy(self.wrapped_model).read()
      file.write(data)
    return load_model(tmp_path)

class PickleableTf:
  def __init__(self, get_model_funcs, *args, **kwargs):
    model_funcs_names = kwargs.get('model_funcs_names', None)
    bytes = kwargs.get('bytes', None)

    if 'model_funcs_names' in kwargs:
      del kwargs['model_funcs_names']
      del kwargs['bytes']

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
    self.bytes = bytes

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
        bytes = self.bytes

        def save():
          nonlocal bytes
          bytes = DirectoryBytesIO(lambda tmp_directory: \
            saver.save(sess, tmp_directory + ckpt_file_name)
          )

        if self.bytes:
          self.bytes.unpack(lambda tmp_directory: \
            saver.restore(sess, tmp_directory + ckpt_file_name)
          )
        else:
          init_op = tf.global_variables_initializer()
          sess.run(init_op)

        result = model_funcs[func_name](sess, save, *args, **kwargs)
        model = PickleableTf(
          self.get_model_funcs,
          *self.args,
          **self.kwargs,
          model_funcs_names=self.model_funcs_names,
          bytes=bytes
        )
        return model, result
