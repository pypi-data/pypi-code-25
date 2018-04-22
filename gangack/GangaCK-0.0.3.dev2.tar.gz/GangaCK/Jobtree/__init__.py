# -*- coding: utf-8 -*-
"""

Jobtree -- Improved visualization of `jobtree` for better jobs organization.

Example::

    ## show current tree.
    >> jt  

    ## Make some directories.
    >> jt mkdir project1
    >> jt mkdir project2

    ## Pointing to certain dir based on their indices,
    # which can be check from ``jt``. Similar to ``cwd`` but transient.
    >> jt 1
    >> jt 2

    ## Make subdir in first dir.
    >> jt 1 mkdir sub1
    >> jt 1 mkdir sub2
  
    ## Rename the dir
    >> jt 1 rename project1-Ztautau
    >> jt 2 rename project2-HiggsMuTau

    ## Using dir index to ``add`` job (by their ID) into dir.
    >> jt 12 add 240 241 242 244

    ## rm the job will only remove the "pointers" in this dir. 
    # The job itself remains intact.
    >> jt 12 rm 244
    
    ## Use ``clean`` to rm all missing jobs from the tree
    >> jt 12 clean

    ## Use ``close`` and ``open`` to better organize the active/archived jobs.
    >> jt 1 close
    >> jt 2 open

"""

## Constants
TAG_CLOSE = ' [CLOSED]'
ROOTDIR   = '/'
C_EMPTY   = '   '
C_BAR     = '|  '
C_BARDASH = '├--'

# C_EMPTY   = u'   '.encode('utf-8')
# C_BAR     = u'⎹  '.encode('utf-8')
# C_BARDASH = u'⎿__'.encode('utf-8')
