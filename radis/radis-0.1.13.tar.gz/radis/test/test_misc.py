# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 14:56:25 2017

@author: erwan

Runs tests for neq/misc so that they can be accessed by pytest (and hopefully 
the CI test suite)

Use
------

Run all tests:

>>> pytest       (in command line, in project folder)

Run only fast tests (i.e: tests that have 'fast' in their name)

>>> pytest -k fast

"""



from __future__ import absolute_import

from __future__ import print_function
def test_config__fast(*args, **kwargs):
    from radis.misc.config import _test
    return _test(*args, **kwargs)
    
def test_utils__fast(*args, **kwargs):
    from radis.misc.utils import _test
    return _test(*args, **kwargs)
    

def _run_testcases(verbose=True, *args, **kwargs):

    test_config__fast(verbose=verbose,*args, **kwargs)
    test_utils__fast(verbose=verbose,*args, **kwargs)
    
    return True

if __name__ == '__main__':
    print(('Testing misc.py: ', _run_testcases(verbose=True)))
    