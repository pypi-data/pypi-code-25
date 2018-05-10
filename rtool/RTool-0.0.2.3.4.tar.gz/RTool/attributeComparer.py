'''RTool/maya/attributeComparer.py

Deployable tool that compares the attributes of a specific node
between two different save states.

Usage:
    The two usage case scenarios::
        1. In Maya script editor, load or paste the script and execute.
        2. Use provided UserSetup.py script to deploy tool to Maya's
           menu bar. Then click Scripts->attributeComparer.py .

Author:
    Ron Nofar

Last updated:
    May 2018 (Check GitHub for exact date and time)
'''

from OptionsWindowBaseClass import OptionsWindow
from functools import partial

import time
import maya.cmds as mc

class AttributeCheckerWindow(OptionsWindow):
    '''Create the attributeComparer Maya GUI window

    The AttributeCheckerWindow class is used to create an object
    instance of an attribute checker window. This class inherits
    from a provided copy of OptionsWindowBaseClass in order to
    mimic the format of a Maya window.

    Usage:
        An AttributeCheckerWindow object is created as such::

            $ object = AttributeCheckerWindow()

        Display the GUI of said object as such::

            $ object.create()

    Note:
        * Check OptionsWindowBaseClass.py for more detail on base
          class implementation.
    '''

    def __init__(self):
        OptionsWindow.__init__(self)
        self.title = "Attribute Checker"
        self.actionName = "Compare and Close"
        self.applyName = "Compare"

        # Set defaults
        self.defaultNodeTextFieldText = "Node Name"

        # Allocate members
        self.dictionaries = [0] * 2
        self.texts = []
        self.textLists = []
        self.currentValues = []
        self.selectedText = None
        self.nodeTextField = None

    def setCurrentValue(self, nodeAttr, *args):
        '''Set the selected attribute's value to field value

        This function is incomplete due to missing functionality
        of cast type. 
        
        Notes:
            * Needs to check for type and cast correctly
            * Can be done with exec()
        '''
        mc.setAttr(
            nodeAttr, mc.textField(
                self.currentValues[3], query=True, text=True))
    
    def textListSelectCommand(self, i, *args):
        '''Set the sibling text scroll list and other variables on selection.

        Args:
            i (int): The index of text scroll list. 0 or 1.

        Note:
            * The *args is only used for ease of use with partial() in
              button's command flag.
        '''
        # Get selected item
        selected = mc.textScrollList(
            self.textLists[i],
            query=True,
            selectItem=True)

        # Set other list to selected
        mc.textScrollList(
            self.textLists[abs(i-1)],
            edit=True,
            selectItem=selected)

        # Set selected Attribute
        mc.text(
            self.selectedText,
            edit=True,
            label="Selected: %s"%selected[0])

        # Set type, value1, value2
        mc.textField(
            self.currentValues[0],
            edit=True,
            text=self.dictionaries[i][selected[0]][1])
        if self.dictionaries[0] != 0:
            mc.textField(
                self.currentValues[1],
                edit=True,
                text=self.dictionaries[0][selected[0]][0])
        if self.dictionaries[1] != 0:
            mc.textField(
                self.currentValues[2],
                edit=True,
                text=self.dictionaries[1][selected[0]][0])

        # Set current value
        tempAttr="%s.%s"%(
            mc.textField(self.nodeTextField, query=True, text=True),
            selected[0])
        tempValue = ""
        try:
            tempValue=mc.getAttr(
                tempAttr,
                silent=True,
                asString=True)
        except (RuntimeError, ValueError, TypeError) as e:
            tempValue="FAILED"

        # Allow for setting attribute value
        mc.textField(
            self.currentValues[3],
            edit=True,
            text=tempValue,
            enable=False if tempAttr is "FAILED" else True,
            enterCommand=partial(self.setCurrentValue, tempAttr))
        
    def setMatrix(self, dictionaries, num, *args):
        '''Create data structure to store incoming attribute information.
        
        This function is used as the command for the "Get Attribute" buttons.

        Args:
            dictionaries ({string:(string,string,string)}): A reference to the
                instance's dictionaries attribute.
            num (int): The index of dictionaries. 0 or 1.

        Note:
            * The *args is only used for ease of use with partial() in
              button's command flag.
        '''
        # Get user input
        nodeText = mc.textField(self.nodeTextField, query=True, text=True)

        # Populate temporary dictionary
        tempDictionary = {}
        if nodeText != self.defaultNodeTextFieldText:
            for i in mc.listAttr(nodeText):
                try:
                    tempDictionary[i] = (
                        mc.getAttr("%s.%s"%(nodeText, i), silent=True, asString=True), 
                        mc.getAttr("%s.%s"%(nodeText, i), silent=True, asString=True, type=True),
                        mc.getAttr("%s.%s"%(nodeText, i), silent=True))
                except (RuntimeError, ValueError, TypeError) as e:
                    tempDictionary[i] = ("FAILED","NONE","FAILED")

        # Save object data
        self.dictionaries[num] = tempDictionary

        # Display attributes
        mc.textScrollList(
            self.textLists[num],
            edit=True,
            append=tempDictionary.keys(),
            selectCommand=partial(self.textListSelectCommand, num))

        # Display last get
        mc.text(
            self.texts[num],
            edit=True,
            label="Last Get: %s"%time.ctime(time.time()))

    def setColumn(self, i):
        '''Create the selection column of the GUI by index.

        Args:
            i (int): The index of column. 0 or 1.
        '''
        mc.columnLayout()
        
        self.textLists.append(
            mc.textScrollList(
                height = 182, width = 256,
                allowMultiSelection=False))

        mc.rowLayout(numberOfColumns=2)
        mc.button(
            label="Get Attributes",
            command=partial(self.setMatrix, self.dictionaries, i))
        self.texts.append(mc.text(label="Last Get: Never", align="right"))
        mc.setParent("..")

        mc.setParent("..")

    def displayOptions(self):
        '''Build the GUI by overriding base class's displayOptions.

        '''
        col = mc.columnLayout(adjustableColumn=True)
        
        self.nodeTextField = mc.textField(
            alwaysInvokeEnterCommandOnReturn=True,
            text=self.defaultNodeTextFieldText)
        
        mc.rowLayout(
            numberOfColumns=2,
            columnAlign=[(1, "center"),(2,"center")])

        self.setColumn(0)
        self.setColumn(1)

        mc.setParent("..")

        mc.separator()

        self.selectedText = mc.text(label="Selected: None")
        mc.rowLayout(numberOfColumns=8)

        # Add custom text field columns
        fieldElements = ("Type","Value 1","Value 2","Current")
        for elm in fieldElements:
            mc.columnLayout()
            mc.text(label=elm)
            mc.setParent("..")
            mc.columnLayout()
            self.currentValues.append(
                mc.textField(text="None", enable=False))
            mc.setParent("..")
        
        mc.setParent("..")
        
        #mc.frameLayout()

        mc.setParent(self.optionsForm)

    def applyBtnCmd(self, *args):
        AttributeComparisonWindow(self.dictionaries)

    def actionCmd(self, *args):
        self.applyBtnCmd()
        self.closeBtnCmd()

class AttributeComparisonWindow:
    titles = ["Attribute Name","Original Value","Changed Value","Value Type"]
    commands = [
        "key", 
        "self.dictionaries[0][key][0]", 
        "self.dictionaries[1][key][0]", 
        "self.dictionaries[1][key][1]"]
    comparisons = {}

    def __init__(self, dictionaries):
        self.dictionaries = dictionaries
        self.check = [0] * len(self.dictionaries[0].keys()) 
        
        win = mc.window(title="Attribute Comparison", resizeToFitChildren=True)
        columns = len(self.titles)
        mc.columnLayout(adj=True)
        mc.frameLayout(label="All values", collapsable=True, width=512)
        mc.scrollLayout(height=256)
        col = mc.rowLayout(numberOfColumns=columns)
        for i in range(columns):
            self.createColumn(i)

        mc.setParent("..")
        mc.setParent("..")

        mc.frameLayout(label="Only changed values", collapsable=True, width=512)
        mc.scrollLayout(height=128)
        col = mc.rowLayout(numberOfColumns=columns)
        
        for i in range(columns):
            self.createColumn(i, True)

        mc.setParent("..")
        
        mc.separator()
        mc.text(label="Note: Frame will be empty upon no changes found.", align="center")

        mc.showWindow(win)

    def handleCommand(self, i, changedOnly=False):
        index = 0
        keys = self.dictionaries[0].keys()
        for key in keys:
            check = False
            exec("tempString = str(%s)"%self.commands[i]) in locals(), globals()
            if i == 1:
                self.comparisons[key] = tempString
            elif i == 2:
                if self.comparisons[key] != tempString:
                    check = True
                    self.check[index] = 1
            if not changedOnly or self.check[index] is 1:       
                tempText = mc.text(label=tempString[:35], height=15)  
                if check:
                    mc.text(
                        tempText,
                        edit=True,
                        font="boldLabelFont",
                        backgroundColor=(1,0.5,0.5))

            index += 1

    def createColumn(self, i, changedOnly=False):
        mc.columnLayout()
        mc.text(label=self.titles[i], font="boldLabelFont")
        mc.separator(height=5, style="in")
        self.handleCommand(i, changedOnly)
        mc.setParent("..")

def main():
    win = AttributeCheckerWindow()
    win.create()

if __name__ == "__main__":
    main()
else:
    exec("def %s():\n\tmain()"
         %os.path.basename(__file__).split('.')[0])
