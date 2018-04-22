#!/usr/bin/env python

"""

Report summary of GeneratorLog.xml from all subjobs of Ganga-Gauss-Job

"""

import os
import re
import sys
import xml.etree.cElementTree as ET
from glob import glob
from collections import Counter

#===============================================================================

def perform_location_check():
  """
  Exit if the location doesn't seem right...
  """
  if re.search(r'/gangadir/workspace/\S+/LocalXML/\d+$',os.getcwd()) is None:
    print 'Bad location, abort: ', os.getcwd()
    sys.exit(-1)

#-------------------------------------------------------------------------------

def read_single_eff(fpath):
  res = dict()
  for _,elem in ET.iterparse( fpath, events=('start',) ):
    if elem.tag == 'efficiency':
      name    = elem.get('name')
      before  = float(elem.find('before').text)
      after   = float(elem.find('after').text)
      res[name + ' before'] = before
      res[name + ' after']  = after
  return res

#-------------------------------------------------------------------------------

def summarize_efficiency():
  count = Counter()
  for fpath in sorted(glob('*/output/GeneratorLog.xml')):
    res = read_single_eff(fpath)
    count += Counter(res)
  print count

  print 'FECa / GLCb: %.3E' % (count['full event cut after'] / count['generator level cut before'])

  pass

#===============================================================================

if __name__ == '__main__':
  perform_location_check()
  summarize_efficiency()
