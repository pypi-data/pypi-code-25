#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   04/13/2005
#
#------------------------------------------------------------------------------

""" Defines a drop target editor for the wxPython user interface toolkit. A
    drop target editor handles drag and drop operations as a drop target.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

import wx

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.drop_editor file.
from traitsui.editors.drop_editor \
    import ToolkitEditorFactory

from pyface.wx.drag_and_drop \
    import PythonDropTarget, clipboard

from text_editor \
    import SimpleEditor as Editor

from constants \
    import DropColor

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(Editor):
    """ Simple style of drop editor, which displays a read-only text field that
    contains the string representation of the object trait's value.
    """

    # Background color when it is OK to drop objects.
    ok_color = DropColor

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        if self.factory.readonly:
            self.control = wx.TextCtrl(parent, -1, self.str_value,
                                       style=wx.TE_READONLY)
            self.set_tooltip()
        else:
            super(SimpleEditor, self).init(parent)
        self.control.SetBackgroundColour(self.ok_color)
        self.control.SetDropTarget(PythonDropTarget(self))

    #-------------------------------------------------------------------------
    #  Returns the text representation of a specified object trait value:
    #-------------------------------------------------------------------------

    def string_value(self, value):
        """ Returns the text representation of a specified object trait value.
        """
        if value is None:
            return ''
        return str(value)

    #-------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #-------------------------------------------------------------------------

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.
        """
        pass

#----- Drag and drop event handlers: -------------------------------------

    #-------------------------------------------------------------------------
    #  Handles a Python object being dropped on the control:
    #-------------------------------------------------------------------------

    def wx_dropped_on(self, x, y, data, drag_result):
        """ Handles a Python object being dropped on the tree.
        """
        klass = self.factory.klass
        value = data
        if self.factory.binding:
            value = getattr(clipboard, 'node', None)
        if (klass is None) or isinstance(data, klass):
            self._no_update = True
            try:
                if hasattr(value, 'drop_editor_value'):
                    self.value = value.drop_editor_value()
                else:
                    self.value = value
                if hasattr(value, 'drop_editor_update'):
                    value.drop_editor_update(self.control)
                else:
                    self.control.SetValue(self.str_value)
            finally:
                self._no_update = False
            return drag_result

        return wx.DragNone

    #-------------------------------------------------------------------------
    #  Handles a Python object being dragged over the control:
    #-------------------------------------------------------------------------

    def wx_drag_over(self, x, y, data, drag_result):
        """ Handles a Python object being dragged over the tree.
        """
        if self.factory.binding:
            data = getattr(clipboard, 'node', None)
        try:
            self.object.base_trait(self.name).validate(self.object,
                                                       self.name, data)
            return drag_result
        except:
            return wx.DragNone

# Define the Text and ReadonlyEditor for use by the editor factory.
TextEditor = ReadonlyEditor = SimpleEditor

### EOF ##################################################################
