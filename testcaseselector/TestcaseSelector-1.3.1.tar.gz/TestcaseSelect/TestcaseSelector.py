from tkinter import *
from tkinter.ttk import Treeview, Style
import unittest


class TestcaseSelector:

    def start(self):

        # Create TK window
        self.root = Tk()
        self.root.style = Style()
        self.root.geometry('800x640')
        self.root.style.configure('Treeview',rowheight=40)

        # Set title and window size
        self.root.wm_title("Select Testcases to Run")

        # Create a frame for the treeview
        self.testcase_frame = Frame(self.root)

        # Create scrollbar for treeview
        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=RIGHT,fill=Y)

        # Create Treeview
        self.treeView = Treeview(self.testcase_frame)
        self.treeView.pack(expand=1,fill=BOTH)

        # Attach scrollbar to Treeview
        self.treeView.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.treeView.yview)


        testcase_dictionary = get_testcase_name_dictonary()
        self.testcase_data = {}
        self.testcase_run_data = {}

        for key in testcase_dictionary.keys():
            subsection = testcase_dictionary[key]

            self.testcase_data[key] = subsection

            s_p = self.treeView.insert('', END, text=key)

            for test in subsection:
                testcase_name = test._testMethodName
                testcase_name = testcase_name
                self.treeView.insert(s_p, END, text=testcase_name)

                self.testcase_run_data[testcase_name] = test

        self.webData = self.testcase_run_data

        # Create buttons for cancel and run tests
        run_button = Button(self.testcase_frame, text="Run", fg="green",command=self._save_selection,width=25,height=5)
        run_button.pack(side=LEFT,expand=1,fill=BOTH)
        quit_button = Button(self.testcase_frame, text="Cancel", fg="red", command=self.treeView.quit,width=25,height=5)
        quit_button.pack(side=RIGHT,expand=1,fill=BOTH)

        self.testcase_frame.pack(expand=1,fill=BOTH)

    def get_tests_from_selected_names(self,names):
        ret_tests = {}
        for name in names:
            ret_tests[name] = self.webData[name]

        return ret_tests

    def _save_selection(self):
        selected_tests = self.treeView.selection()

        output=[]
        for selection in selected_tests:
            item_text = self.treeView.item(selection,'text')
            if 'test_' in item_text:
                if item_text not in output:
                    output.append(item_text)
                else:
                    pass
            elif 'Tests' in item_text:
                for test in self.testcase_data[item_text]:
                    output.append(test._testMethodName)
                # output = output + self.testSectionData[item_text]

        self.testcases = self.get_tests_from_selected_names(output)
        self.root.quit()

    def get_testcases(self):
        self.start()
        self.root.mainloop()
        self.root.destroy()

        # Try/Except to fail gracefully
        try:
            return self.testcases
        except:
            exit(0)

def test_name(parent):
    tns = []
    if hasattr(parent, '_testMethodName'):
        return parent
    elif hasattr(parent, '_tests'):
        for t in parent._tests:
            tn = test_name(t)
            if tn:
                tns.append(tn)
    return tns

def get_all_automated_tests():

    loader = unittest.TestLoader()
    tests = loader.discover('Tests', pattern='*Tests.py')

    tcs = [y for x in [y for x in test_name(tests) for y in x] for y in x]

    return tcs

def get_testcase_name_dictonary():

    all_tests = get_all_automated_tests()

    section_dict = {}

    for test in all_tests:
        testcase_name = test
        test_section = type(test).__name__

        if test_section in section_dict:
            section_dict[test_section].append(testcase_name)
        else:
            section_dict[test_section] = [testcase_name]

    return section_dict

# # Testing code -- needs a Tests directory with a .py file containing unit-test to work
# tcs = TestcaseSelector()
# tests = tcs.get_testcases()
# print(1)