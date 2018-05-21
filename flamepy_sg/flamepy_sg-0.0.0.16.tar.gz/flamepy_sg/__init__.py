# import os
# import sys


'''
try:
    root_path = os.environ['DL_PYTHON_HOOK_PATH']
except:
    import traceback
    traceback.print_exc()
'''

'''
absolute_path = os.path.realpath(__file__)
root_path = '/'.join(absolute_path.split('/')[0:-1])
print '-' * 80
print "main module's (FlamePy_sg) __init__: "
# print "absolute_path for top __init__.py: ", absolute_path
print "root_path extracted from os.environ['DL_PYTHON_HOOK_PATH']: ", root_path
print '-' * 80
'''

# for clique and yaml imports > not sure if this is needed anymore. > apparently not needed.
# sys.path.append("{root}/modules".format(root=root_path))
