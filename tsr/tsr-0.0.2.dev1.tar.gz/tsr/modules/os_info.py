import os, json, shutil
from requests import get as requests_get
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
        shutil.copyfileobj(request.raw, f)

def writeif(path, content, readonly=False, **kwargs):
    if readonly:
        return # Avoid writes
    # Defaults
    append=False
    # kwargs overrides
    if 'append' in kwargs.keys():
        append=True
    # Main
    if append:
        with open(path, 'a') as f:
            f.write(content)
    else:
        with open(path, 'w') as f:
            f.write(content)

def mkdir(path):
    try:
        os.makedirs(path)
    except: # Already exists, we don't care about erroring out if it exists.
        pass

def touch(path):
    if not os.path.isfile(path):
        pathlib_Path(path).touch() # NB: exist_ok=True should also not overwrite the file, but does overwrite metadata

def bytes_to_human_readable(n_bytes):
    if n_bytes < 0:
        return '-'+positive_bytes_to_human_readable(n_bytes)
    else:
        return positive_bytes_to_human_readable(n_bytes)

def positive_bytes_to_human_readable(n_bytes):
    n_bytes=float(n_bytes)
    units=['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
    i=0
    while n_bytes>1024:
        i+=1
        n_bytes/=1024.0
    unit=units[i]
    n_bytes=round(n_bytes, 3)
    return str(n_bytes) + ' ' + unit

def memory_usage_raw():
    # This function is entirely the work of Martin Geisler of StackOverflow: https://stackoverflow.com/users/110204/martin-geisler, May 2009
    status=None
    result={'peak': 0, 'rss': 0}
    try:
        # This will only work on systems such as Linux with a /proc file system
        status=open('/proc/self/status')
        for line in status:
            parts=line.split()
            key=parts[0][2:-1].lower()
            if key in result:
                result[key]=int(parts[1])
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

def cp(src, dst):
    try:
        shutil.copytree(src, dst)
    except:
        shutil.copy(src, dst)


file_location=os.path.join(os.path.expanduser('~'), '.config', 'tsr', 'paths.json')
root_dir=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
default_path_settings=os.path.join(root_dir, 'settings')
if os.path.isfile(file_location):
    paths=json.load(open(file_location, 'r'))
else: # Defaults
    paths={
        'main':root_dir,
        'posts':os.path.join(root_dir, 'posts'),
        'threads':os.path.join(root_dir, 'threads'),
        'threads_json':os.path.join(root_dir, 'threads.json'),
        'forums':os.path.join(root_dir, 'forums'),
        'users':os.path.join(root_dir, 'users'),
        'users_json':os.path.join(root_dir, 'users.json'),
        'avatars':os.path.join(root_dir, 'avatars'),
        'settings':os.path.join(os.path.expanduser('~'), '.config', 'tsr'),
        'images':os.path.join(os.path.expanduser('~'), 'Pictures', 'tsr'),
        'log':os.path.join(root_dir, 'log.txt')
    }
    cp(default_path_settings, paths['settings'])
    with open(file_location, 'w') as f:
        json.dump(paths, f)
        
path_variables_str=' '.join([path for path in paths.keys()])
PathObject=namedtuple('path', path_variables_str)
path=PathObject(**paths)
del path_variables_str

if not os.path.isdir(path.settings):
    cp(default_path_settings, path.settings) # copy default settings into new settings path

for key in paths.keys(): # Make the remaining (empty) folders
    object_path=paths[key]
    if object_path.split('.')[-1] not in ['json', 'txt']:
        mkdir(object_path)
    else:
        touch(object_path)
