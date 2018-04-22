#!/usr/bin/env python
"""

Helper script to print out all cached entries by this package.

"""

from PythonCK import logger

TEMPLATE = '{:120.120} | {:.17}'

def simplestring(argskwargs):
  """
  Return simple string, if possible, from given raw tuple (args,kwargs).
  """
  args,_ = eval(argskwargs)
  if len(args)==1 and isinstance(args[0], basestring):
    return args[0]
  return None

def main():
  with logger.capture():
    import GangaCK

  list_func = [
    GangaCK.IOUtils.get_raw_list_LFN,
    GangaCK.IOUtils.get_catalog_bkq,
  ]
  for func in list_func:
    print func.__name__
    for rawkey,(val,mtime) in func.shelf.iteritems():
      print TEMPLATE.format( simplestring(rawkey), func.timeleft( rawkey ) )
  

if __name__ == '__main__':
  main()
