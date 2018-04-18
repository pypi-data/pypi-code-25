from __future__ import absolute_import

import os

from traits.testing.unittest_tools import unittest

from ..directory_dialog import DirectoryDialog
from ..gui import GUI
from ..toolkit import toolkit_object

GuiTestAssistant = toolkit_object('util.gui_test_assistant:GuiTestAssistant')
no_gui_test_assistant = (GuiTestAssistant.__name__ == 'Unimplemented')

ModalDialogTester = toolkit_object('util.modal_dialog_tester:ModalDialogTester')
no_modal_dialog_tester = (ModalDialogTester.__name__ == 'Unimplemented')


@unittest.skipIf(no_gui_test_assistant, 'No GuiTestAssistant')
class TestDirectoryDialog(unittest.TestCase, GuiTestAssistant):

    def setUp(self):
        GuiTestAssistant.setUp(self)
        self.dialog = DirectoryDialog()

    def tearDown(self):
        if self.dialog.control is not None:
            with self.delete_widget(self.dialog.control):
                self.dialog.destroy()
        GuiTestAssistant.tearDown(self)

    def test_create(self):
        # test that creation and destruction works as expected
        self.dialog._create()
        self.gui.process_events()
        self.dialog.destroy()

    def test_destroy(self):
        # test that destroy works even when no control
        self.dialog.destroy()

    def test_close(self):
        # test that close works
        self.dialog._create()
        self.gui.process_events()
        self.dialog.close()

    def test_default_path(self):
        # test that default path works
        self.dialog.default_path = os.path.join('images', 'core.png')
        self.dialog._create()
        self.gui.process_events()
        self.dialog.close()

    def test_no_new_directory(self):
        # test that block on new directories works
        self.dialog.new_directory = False
        self.dialog._create()
        self.gui.process_events()
        self.dialog.close()

    def test_message(self):
        # test that message setting works
        self.dialog.message = 'Select a directory'
        self.dialog._create()
        self.gui.process_events()
        self.dialog.close()

    #XXX would be nice to actually test with an open dialog, but not right now
