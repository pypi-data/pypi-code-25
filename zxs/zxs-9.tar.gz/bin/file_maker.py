#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  6 15:16:37 2018

@author: zxs107020
"""

import sys
import os
import json
import zxs
import pandas as pd

# Show stage in program
sys.stdout.write("Setting directories...")
sys.stdout.flush()
sys.stdout.write("\n")
sys.stdout.flush()

# System defined arguments

# Working directory
wd = str(sys.argv[1])

os.chdir(wd)

# In-file
fn = str(sys.argv[2])

# System arguments
kwargs = json.loads(sys.argv[3])

# Data Processing

# Display process in console
sys.stdout.write("Loading Data...")
sys.stdout.flush()
sys.stdout.write("\n")
sys.stdout.flush()

# Load and parse the in-file
data = zxs.local_import(wd, fn)

# Display process in console
sys.stdout.write("Transforming Data...")
sys.stdout.flush()
sys.stdout.write("\n")
sys.stdout.flush()

# Transform to numeric
zxs.transform(data, **kwargs)

# Display process in console
sys.stdout.write("Writing file...")
sys.stdout.flush()
sys.stdout.write("\n")
sys.stdout.flush()

# Out-file
data.to_csv('numeric_file.csv')

# Display process in console
sys.stdout.write("Process Complete")
sys.stdout.flush()
sys.stdout.write("\n")
sys.stdout.flush()