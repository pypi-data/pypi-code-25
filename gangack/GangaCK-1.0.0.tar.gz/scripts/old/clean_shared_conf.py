#!/usr/bin/env python

import re
import os
import shutil
from glob import glob

# 1st-pass: Get conf used by the job
set_conf = set()
for fname in glob('repository/khurewat/LocalXML/6.0/jobs/*/*/data'):
  with open(fname) as fin:
    conf = re.findall(r"ShareDir\(name='(.*)',subdir", fin.read())[0]
    set_conf.add(conf)

# 2nd-pass, find redundant ones
set_local = set(os.listdir('shared/khurewat'))

### 
list_redundant = sorted(set_local - set_conf)
print 'Redundant locals:'
for x in list_redundant:
  print x
  src = os.path.join('shared/khurewat',x)
  dst = os.path.join('shared/_redundant',x)
  shutil.move(src, dst)

