#!/usr/bin/env python

import os
import re
import argparse
from glob import iglob as glob
from collections import defaultdict

from PythonCK import logger

FNAME = '__postprocesslocations__'

def regex_jid(fpath):
  return int(re.findall(r'LocalXML/(\d+)', fpath )[0])

def regex_lfns(fpath):
  with open(fpath) as fin:
    dat = fin.read()
  return re.findall( r'DiracFile:::.*->(\S+):::\[', dat )

def Step01(root):
  ## 1st-Pass: collect all files, indexed by JID
  logger.info('Collect list of files, index by JID.')
  logger.info('Please wait...')
  res   = defaultdict(list)  # List of LFNs, index by JID
  paths = []
  paths.append(os.path.join( root, '*/output'  , FNAME ))
  paths.append(os.path.join( root, '*/*/output', FNAME ))
  for path in paths:
    for fpath in glob(path):
      res[regex_jid(fpath)].append( fpath )
  njobs  = len(res)
  nfiles = sum(len(l) for l in res.values())
  logger.info('Collecting completed. %i jobs, %s files' % (njobs, nfiles))
  return res


def Step02(res):
  ## 2nd-Pass: Resolve all files.
  logger.info('Start listing lfns')
  for jid,l in dict(res).iteritems():
    logger.info('Reading jid: %i' % jid )
    lfns = []
    for fpath in l:
      lfns.extend(regex_lfns( fpath ))
    res[jid] = lfns 
  return res

def main(args):
  ## Quiet import
  with logger.capture():
    from GangaCK import ConfigUtils

  res = Step01(ConfigUtils.dir_workspace())
  res = Step02(res)

  if args.flatten:
    for lfns in res.values():
      for lfn in lfns:
        print lfn 
  else:
    print res


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--flatten', action='store_true', default=False, help='If True, return a flatten list: One lfn per line. Discard JID information.')
  args = parser.parse_args()
  main(args)
