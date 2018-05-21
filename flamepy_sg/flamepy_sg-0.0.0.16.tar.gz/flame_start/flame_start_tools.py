import os
import sys


absolute_path = os.path.realpath(__file__)
top_parent_path = '/'.join(absolute_path.split('/')[0:-2])

print '>>>>>>>>>>>>>> ABSOLUTE PATH >>>>>>>>>>>>>>>>>> :', absolute_path
print '>>>>>>>>>>>>>> TOP PARENT PATH >>>>>>>>>>>>>>>>>> :', top_parent_path

# sys.path.append("{root}/flamepy_sg".format(root=root_path))
sys.path.append("{root}".format(root=top_parent_path))
# sys.path.append('/disks/nas0/CGI/R_n_D/work.stefan/src/flame')

#from flamepy_sg.scripts import getCustomUIActions
from flamepy_sg.scripts.CUA_tools import *
# from flamepy_sg.modules import clique # didn't help. I fucking hate clique


'''
print '-' * 80
print "Flame_start.py - print 'sys.path'"
print (sys.path)
print '-' * 80
'''
