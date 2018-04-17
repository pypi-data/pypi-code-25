import os, json
from requests import get as requests_get
from shutil import copyfileobj as shutil_copyfileobj
from pathlib import Path as pathlib_Path
from collections import namedtuple
if os.name!='posix':
    try:
        from psutil import Process
        use_psutil=True
    except ImportError: # psutil is nice to have but not necessary
        use_psutil=False

def download_file(url, *args):
    if args:
        destination=args[0]
    else:
        destination=os.getcwd()
    basename=url.split('/')[-1]
    request=requests_get(url, stream=True)
    with open(os.path.join(destination, basename), 'wb') as f:
        shutil_copyfileobj(request.raw, f)

def mkdir(path):
    try:
        os.makedirs(path)
    except: # Already exists, we don't care about erroring out if it exists.
        pass

def touch(path):
    if not os.path.isfile(path):
        pathlib_Path(path).touch() # NB: exist_ok=True should also not overwrite the file, but does overwrite metadata

def bytes_to_human_readable(number_of_bytes):
    # Credit: https://stackoverflow.com/users/1350091/grzegorz-bazior, May 2016
    if number_of_bytes < 0:
        raise ValueError("!!! number_of_bytes can't be smaller than 0 !!!")
    step_to_greater_unit = 1024.
    number_of_bytes = float(number_of_bytes)
    unit = 'bytes'
    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'KB'
    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'MB'
    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'GB'
    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'TB'
    precision = 1
    number_of_bytes = round(number_of_bytes, precision)
    return str(number_of_bytes) + ' ' + unit

def memory_usage_raw():
    # Credit: https://stackoverflow.com/users/110204/martin-geisler, May 2009
    status = None
    result = {'peak': 0, 'rss': 0}
    try:
        # This will only work on systems with a /proc file system
        # (like Linux).
        status = open('/proc/self/status')
        for line in status:
            parts = line.split()
            key = parts[0][2:-1].lower()
            if key in result:
                result[key] = int(parts[1])
    finally:
        if status is not None:
            status.close()
    return result

def memory_usage():
    if os.name=='posix': # linux
        d=memory_usage_raw()
        peak=bytes_to_human_readable(d['peak']*1024) # Linux proc is in KB
        rss=bytes_to_human_readable(d['rss']*1024)
        return {'peak':peak, 'rss':rss}
    elif use_psutil:
        process=Process(os.getpid())
        return process.memory_info()
    return cl.red+'psutil not installed'+cl.end




file_location=os.path.join(os.path.expanduser('~'), 'tsr_paths.json')
if os.path.isfile(file_location):
    paths=json.load(open(file_location, 'r'))
else:
    root_dir=os.path.join(os.path.expanduser('~'), 'sites', 'tsr')
    paths={
        'main':root_dir,
        'posts':os.path.join(root_dir, 'posts'),
        'threads':os.path.join(root_dir, 'threads'),
        'forums':os.path.join(root_dir, 'forums'),
        'users':os.path.join(root_dir, 'users'),
        'settings':os.path.join(root_dir, 'settings'),
        'images':os.path.join(root_dir, 'images'),
        'log':os.path.join(root_dir, 'log.txt')
    }
    with open(file_location, 'w') as f:
        json.dump(paths, f)
    for key in paths.keys():
        object_path=paths[key]
        if '.' not in object_path:
            mkdir(object_path)
        else:
            touch(object_path)
        
path_variables_str=' '.join([path for path in paths.keys()])
PathObject=namedtuple('path', path_variables_str)
path=PathObject(**paths)
del path_variables_str
