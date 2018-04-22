#!/usr/bin/env python

"""
Quick script to read the content in Ganga's JobTree offline.
"""

import argparse
from GangaCK import Jobtree
from GangaCK.Jobtree.OfflineJobtreeReader import OfflineJobtreeReader

def get_parser():
  parser = argparse.ArgumentParser(
    description=Jobtree.__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v', '--ignore-closed', action='store_true', 
    help='If True, show all jobs regardless the directory CLOSED status.')
  return parser

def main():
  ## Quiet import
  from PythonCK import logger
  logger.setLevel(logger.ERROR)
  # with logger.capture():

  ## Write out, using adapter
  args = get_parser().parse_args()
  print OfflineJobtreeReader().__str__(ignore_closed=args.ignore_closed)

if __name__ == '__main__':
  main()
