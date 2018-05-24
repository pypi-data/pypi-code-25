import os
import subprocess

p = subprocess.Popen('ls', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
    print line,
retval = p.wait()

DIR = 'cv'

os.chdir()
files = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)
