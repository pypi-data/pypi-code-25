import os
import sys


absolute_path = os.path.realpath(__file__)
top_parent_path = '/'.join(absolute_path.split('/')[0:-2])

print '>>>>>>>>>>>>>> ABSOLUTE PATH >>>>>>>>>>>>>>>>>> :', absolute_path
print '>>>>>>>>>>>>>> TOP PARENT PATH >>>>>>>>>>>>>>>>>> :', top_parent_path

sys.path.append("{root}".format(root=top_parent_path))
from flamepy_sg.scripts.CUA_apps import *

print '-' * 80
print "Flame_start.py - print 'sys.path'"
print (sys.path)
print '-' * 80
