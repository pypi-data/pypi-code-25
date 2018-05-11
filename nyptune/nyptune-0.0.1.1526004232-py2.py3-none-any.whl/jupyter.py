from subprocess import *
from pathlib import Path
import os

def presave(path, model, contents_manager):
    magix = model['content']['metadata''']['magix'] = {}
    conda = run(["conda", "list", "--explicit"], stdout = PIPE, encoding = 'utf-8', shell=False)
    magix['conda'] = conda.stdout.split('\n')
    pip = run(["pip", "list", "--format", "freeze"], stdout = PIPE, encoding = 'utf-8', shell = False)
    magix['pip'] = pip.stdout.split('\n')
    path = Path(path)
    cache = path.parent / '.cache'
    os.makedirs(cache, exist_ok = True)
    procs = []
    magix['cache']={}
    ipfs = run(["ipfs", "add", "--nocopy", "-r", str(cache)], stdout = PIPE, encoding = 'utf-8', shell = False)
    for line in ipfs.stdout.strip().split('\n'):
        action, sig, name = line.split()
        magix['cache'][name] = sig