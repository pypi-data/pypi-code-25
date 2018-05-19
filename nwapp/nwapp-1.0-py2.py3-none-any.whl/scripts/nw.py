

import os
import sys
import argparse
from contract_process import *
from pymongo import MongoClient
from pprint import pprint
import datetime


'''
Positional arguments without hyphen
Optional arguments with hyphen (single for short.. double for expander)
help for each argument help= "...."
type for each argument type=str or type=int
default value for optional arguments default=0
action value for optional argumetn action="store_action"
'''
'''
parser = argparse.ArgumentParser()
parser.add_argument()
args = parser.parse_args()
'''

if __name__ == '__main__':

    
    