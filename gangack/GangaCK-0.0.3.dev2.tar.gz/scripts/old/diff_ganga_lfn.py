#!/usr/bin/env python

"""
Read all lfn belongs to Ganga
"""

import re
import os

from glob import glob
from MyPythonLib import log
from MyPythonLib.Decorators import cache_to_file
# log.setLevel(log.DEBUG)

### NOTE: BE VERY CAREFUL on this pattern. 
###       If tha pattern failed to secure some file, they'll be deleted this way!
# <attribute name="lfn"> <value>'/lhcb/user/c/ckhurewa/2014_11/90521/90521934/Gauss-42100000-100ev-20141108.sim'</value>
pattern = r"""<attribute name="lfn"> <value>'(.*)'"""

LFN_ALL   = '/home/khurewat/PhD_Analysis/lhcb-user-c-ckhurewa.lfns'
LFN_GANGA = '/home/khurewat/gangadir/ganga-lhcb-user-c-ckhurewa.csv'
LFN_DIFF  = '/home/khurewat/gangadir/diff-lhcb-user-c-ckhurewa.lfns'

WHITELIST = {
  '/lhcb/user/c/ckhurewa/MyPythonLib.zip',
}

# @cache_to_file(timeout=3600)
def findall_in_file(fpath):
  """Given the data file to read, return list of lfn found inside, cleaned."""
  log.debug('Reading fpath: '+fpath)
  with open(fpath) as fin:
    results = re.findall(pattern, fin.read())
    return [ x for x in results if x ]  

# @cache_to_file(filter=lambda _,y: y)
@cache_to_file(input_skip_write=lambda _,y: not y)
def findall_in_dir(root, is_jdir):
  """ RECURSIVE. Flag is_jdir to True if this is jdir (ignore subjobs)"""
  result = []
  for name in os.listdir(root):
    fullpath = os.path.join(root, name)
    if os.path.isfile(fullpath):
      if name=='data':
        result.extend(findall_in_file(fullpath))
    else:
      result.extend(findall_in_dir(fullpath, False))
  return result

def list_lfn():
  path = '/home/khurewat/gangadir/repository/khurewat/LocalXML/6.0/jobs/*/*/'
  for jdir in sorted(glob(path)):
    log.debug('Reading jdir: '+jdir)
    jid = jdir.split('/')[-2]
    for result in findall_in_dir(jdir, True):
      yield jid,result

def main_write_csv():
  with open(LFN_GANGA, 'w') as fout:
    for jid,lfn in list_lfn():
      log.debug(lfn)
      fout.write(jid+','+lfn+'\n')
  log.info('Write output to: '+LFN_GANGA)

def main_diff():
  with open(LFN_ALL) as f1:
    with open(LFN_GANGA) as f2:
      s1 = set([x.strip()       for x in f1.readlines()])
      s2 = set([x.split(',')[1] for x in f2.readlines()])
  log.info('Count LFN_ALL  : %r'%len(s1))
  log.info('Count LFN_GANGA: %r'%len(s2))
  with open(LFN_DIFF, 'w') as fout:
    for lfn in sorted(list(s1-s2-WHITELIST)):
      log.debug(lfn)
      fout.write(lfn+'\n')
  log.info('Write the diff file to: '+LFN_DIFF)


if __name__ == '__main__':
  main_write_csv()
  # main_diff()