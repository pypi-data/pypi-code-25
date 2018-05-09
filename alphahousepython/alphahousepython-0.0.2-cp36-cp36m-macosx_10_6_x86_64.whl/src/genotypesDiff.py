#!/usr/bin/python2.7
# encoding: utf-8





import numpy as np
import sys


x = np.loadtxt(sys.argv[1])
y = np.loadtxt(sys.argv[2])


for a,b in zip(x,y):
    for index,(a1,b1) in enumerate(zip(a,b),start=1):
        if (a1 != b1):
            print("ID:" + str(a[0]) +  " " + str(a1) +" " + str(b1) + " SNP:" + str(index))
