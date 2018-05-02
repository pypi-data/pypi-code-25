import sys
import os.path
import os
import time
import uuid
import json
import multiprocessing as mp
import atexit

session = uuid.uuid4().hex
machine = None
once = True
_enabled = True
proc = None
site = os.environ.get("LRS") or "https://learning-rates.com" 
chunk_list = mp.Manager().list()
session_file = os.path.expanduser('~/.lr')

if not os.path.exists(session_file):
  with open(session_file, "w") as sfile:
    sfile.write(uuid.uuid4().hex)


with open(session_file, "r") as sfile:
  machine=sfile.read()

def new_session(hyperparams=None):
    global session
    session = uuid.uuid4().hex
    global hyper 
    hyper = {}
    global once
    once = True
    global chunk_list
    chunk_list = mp.Manager().list()
    global proc
    if proc is not None and proc.is_alive():
        proc.terminate()

    if hyperparams is not None:
        send(hyperparams)

def sending_process(chunk_list):
  import requests
  import zlib
  PY3 = sys.version_info[0] == 3
  string_type = str if PY3 else basestring

  s = requests.Session()
  s.headers.update({
    'machine': machine, 
    })
  cur_chunk = {}
  finish = False
  cons_fails = 0

  bin_dict = {}
  try:
    while not finish:
      while len(chunk_list) > 0:
        arg_dict = {}
        args, now = chunk_list.pop(0) 
        if args is None:
          finish = True
          break
        if len(args) == 2:
          arg_dict[args[0]] = args[1]
        elif isinstance(args[0], dict): 
          arg_dict = args[0]
        else:
          raise Exception("wrong arguments")
        
        arg_dict_filter = {}
        for name in arg_dict:
          #str_type = str(type(arg_dict[name]))
          if isinstance(arg_dict[name], bool) or isinstance(arg_dict[name], int) or isinstance(arg_dict[name], float) or isinstance(arg_dict[name], string_type):
            arg_dict_filter[name] = arg_dict[name]
          elif isinstance(arg_dict[name], (bytes, bytearray)):
              atype, aname = name.split(':')
              if atype == 'audio':
                  filename ="{}.wav".format(aname) 
                  bin_dict[aname] = (filename, arg_dict[name], "audio/wav")
                  arg_dict_filter[name] = filename
              elif atype == 'image':
                  filename ="{}.png".format(aname) 
                  bin_dict[aname] = (filename, arg_dict[name], "image/png")
                  arg_dict_filter[name] = filename
              #if atype == 'audio':
            
          #TODO: numpy
          #elif str_type == "<type 'numpy.float16'>" 
            
        arg_dict = arg_dict_filter

        for name in arg_dict:
          if not (name in cur_chunk):
            cur_chunk[name] = [(arg_dict[name], now)]
          else: 
            cur_chunk[name].append((arg_dict[name], now))

      if len(cur_chunk) > 0 or len(bin_dict) > 0:
        try:
          if len(bin_dict) > 0:
            r = s.post("{0}/data/{1}".format(site, session), files=bin_dict, timeout=5.0)
            bin_dict = {}
          if len(cur_chunk) > 0:
            r = s.post("{0}/data/{1}".format(site, session), data=json.dumps(cur_chunk), timeout=5.0, headers={ 'Content-Type' : 'application/octet-stream'})
            cur_chunk={}
          cons_fails = 0
        except Exception as e:
          cons_fails += 1
          print("learning-rates.com: error sending data", e)
          if cons_fails >= 6:
            print("learning-rates.com: Too many connection problems, stop sending.")
            finished = True
      if not finish:
        time.sleep(1)
  except: 
    e = sys.exc_info()[0]
    print("learing-rates.com: ", e) 

hyper = {}
def log_hyperparams(d):
  to_send = {}
  for name in d:
    if not (name in hyper):
      hyper[name] = d[name]
      to_send[name] = d[name]

  send(to_send)

def send(*args):
  if not _enabled:
    return
  global once
  global proc
  if once:
    proc = mp.Process(target=sending_process, args=(chunk_list,))
    proc.start()
    once = False
    print("lrs: open {} to view the progress".format(get_url())) 

  if proc.is_alive():
    chunk_list.append((args, time.time()))

def log(*args):
    send(*args)

def log_src(*filenames):
    for filename in filenames:
        try:
            st = os.stat(filename)
            #print(st)
            if st.st_size > 1e+6:
                print("lrs: this file is too big to send (> 1mb) {}", filename)
                continue
            
            send("file:{}".format(filename), open(filename, 'r').read())
        except FileNotFoundError:
            print("lrs: file not found {}".format(filename))

def log_audio(name, tensor, sample_rate=16000, clip=(-1, 1)):
    if not _enabled: 
        return
    import numpy as np
    import io
    import wave

    tensor = tensor.squeeze().clip(clip[0], clip[1]) * (2 ** 15)
    tensor = tensor.astype('<i2')
    assert(tensor.ndim == 1), 'input tensor should be 1 dimensional.'

    fio = io.BytesIO()
    write = wave.open(fio, 'wb')
    write.setnchannels(1)
    write.setsampwidth(2)
    write.setframerate(sample_rate)
    write.writeframes(tensor.tobytes())
    write.close()
    audio_string = fio.getvalue()
    fio.close()
    send("audio:{}".format(name), audio_string)

def log_image(name, tensor, clip=(-1, 1)):
    if not _enabled: 
        return
    assert(tensor.ndim == 3), 'input tensor should be 3 dimensional.'
    import numpy as np
    from PIL import Image
    import io
    #clip and -> [0, 1]
    if clip is not None:
        tensor = tensor.clip(clip[0], clip[1]) - clip[0]
        tensor = tensor / (clip[1] - clip[0])
    tensor *= 256
    img = Image.fromarray(tensor.astype('uint8'), 'RGB')
    fio = io.BytesIO()
    img.save(fio, format='PNG')
    send("image:{}".format(name), fio.getvalue())
    fio.close()

exit_code = None
exit_exc = None
original_exit = sys.exit
original_exc = sys.excepthook

def exc_handler(exc_type, exc, *args):
  global exit_exc
  exit_exc = exc_type
  if original_exc is not None:
    original_exc(exc_type, exc, *args)

def my_exit(code=0):
    global exit_code
    exit_code = code
    original_exit(code)

sys.exit = my_exit
sys.excepthook = exc_handler

def on_exit():
  if proc is None:
    return

  if exit_exc is None and exit_code == 0:
    proc.join()
  else:
    proc.terminate()

def enabled(value):
  global _enabled
  _enabled = value

def get_url(): 
  return "{0}/m/{1}".format(site, machine[:6])

def main():
  print("Open {} to view expriments that run from this box".format(get_url())) 

atexit.register(on_exit)
__all__ = ['send', 'enabled', 'get_url', 'log_src', 'log', 'log_hyperparams', 'log_audio', 'log_image']
