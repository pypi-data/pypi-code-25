#!/usr/bin/env python

"""

| JID    | backend.actualCE | Latest | Timestamp [UTC]             | Time elapsed | 
| 4164.8 |                  | 45     | 2016-02-22 19:02:50.043703  | 55:44:57     |

"""

import re
import string # for missing-key formatter
from collections import defaultdict
from GangaCK import GPI

header   = '|   JID    | backend.actualCE | Latest | Timestamp [UTC]             | Time elapsed |'
template = '| {JID:8} | {actualce:16} | {latest:6} | {timestamp:27} | {elapsed:12} |'

def queue():
  """
  Check for appname with select is slow. Hack with ._impl
  """
  for j in GPI.jobs.select(status='running').select(backend='Dirac'):
    if j.application._impl._name == 'Gauss':
      if j.subjobs:
        for sj in j.subjobs.select(status='running'):
          yield sj
      else:
        yield j

def parse(stdout):
  if 'Watchdog is initializing' in stdout:
    return {}
  lines     = stdout.strip().split('\n')
  timestamp = re.findall(r' on (.*) \[UTC\]', lines[1])[0]
  elapsed   = re.findall(r' is (\S+)', lines[2])[0]
  latest    = re.findall(r'job = (\d+) ', lines[-1])
  latest    = latest[0] if latest else ''
  del stdout, lines
  return locals()

def fetch(j):
  JID       = re.findall(r'LocalXML/(\S+)/input', j.inputdir)[0].replace('/','.')
  actualce  = j.backend.actualCE
  res       = defaultdict(str, **locals())
  response  = GPI.diracAPI("peek(%i)"%j.backend.id)
  if response['OK']:
    res.update(parse(response['Value']))
  return res

def node_print_header():
  print 
  print header
  print '-'*97

def node_print(j):
  print string.Formatter().vformat(template, (), fetch(j))

def jv_dirac_gauss():
  GPI.queues.add(node_print_header)
  for j in queue():
    GPI.queues.add(node_print, (j,))

#===============================================================================

if __name__ == '__main__':
  # jv_dirac_gauss()
  pass
