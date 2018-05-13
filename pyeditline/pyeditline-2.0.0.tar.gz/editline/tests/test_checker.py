import sys
import re
import unittest
from test.support import import_module

# just grab what we need from the other...
from editline.tests.test_lineeditor import CompletionsBase, CompletionsCommon

class CompMixIn_InCall(object):
    '''Run the same test as before but do the completion within a call: print(<stuff>'''
    def __init__(self):
        prefix = 'print('
        self.cmd = prefix + self.cmd + ')'
        self.cmd_tab_index += len(prefix)

class CompMixIn_InCall_w_Space(object):
    '''Run the same test as before but do the completion within a call: print( <stuff>'''
    def __init__(self):
        prefix = 'print( '
        self.cmd = prefix + self.cmd + ')'
        self.cmd_tab_index += len(prefix)

class CompMixIn_InAssignment(object):
    '''Run the same test as before but do the completion within a call: print( <stuff>'''
    def __init__(self):
        prefix = 'x = '
        self.cmd = prefix + self.cmd
        self.cmd_tab_index += len(prefix)
        self.result = None

class CompMixIn_InAssignment_and_InCall(CompMixIn_InAssignment, CompMixIn_InCall):
    def __init__(self):
        CompMixIn_InCall.__init__(self)
        CompMixIn_InAssignment.__init__(self)

#class WeirdExtension(CompletionsBase,CompMixIn_InAssignment_and_InCall):
#    def __init__(self, *args):
#        print("WExt: __init__")
#        CompletionsBase.__init__(self, *args)
#        CompMixIn_InAssignment_and_InCall.__init__(self)


# class CB_InCall(CompletionsBase):
#     def __init__(self, *args):
#         super().__init__(*args)
#         print("DBG: CB_InCall.__init__()")

#         prefix = 'print('
        
#         self.cmd = prefix + self.cmd + ')'
#         self.cmd_tab_index += len(prefix)
        

#import unittest

#from ourapp.functions import is_user_error
# def is_user_error(sc):
#     if 440 > sc > 430:
#         return False
#     return True

# class IsUserErrorTestCase(unittest.TestCase):

#     def setUp(self):
#         super().setUp()
#         print("DBG: setUp()")

#     def tearDown(self):
#         print("DBG: tearDown()")
#         super().tearDown()
    
#     def test_yes(self):
#         """User errors return True."""
#         for status_code in range(400, 499):
#             with self.subTest(status_code=status_code):
#                 self.assertTrue(is_user_error(status_code))

if __name__ == "__main__":
    unittest.main()
