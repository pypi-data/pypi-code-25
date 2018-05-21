
import subprocess
import os
import sys

from flamepy_sg.scripts.customprints.ansi_colors import sg_colors

absolute_path = os.path.realpath(__file__)
root_path = '/'.join(absolute_path.split('/')[0:-3])


def my_test_print():

    # print "\x1b[38;5;82m --- Begining of test_print2.py --- \x1b[0m"
    print sg_colors.blue2 + "--- Begining of test_print2.py ---" + sg_colors.endc

    print sg_colors.grey3 + "TEST PRINT: should come from the callback ('callback': _testprint) in Snippets_list_dict.py"
    print "It should also open a text file" + sg_colors.endc

    # navigate down to the desired folder
    file_path = "{root}/scripts/batch_snippets/open_me_test.rtf".format(root=root_path)
    print sg_colors.yellow1 + file_path + sg_colors.endc

    subprocess.call(["open", file_path])
