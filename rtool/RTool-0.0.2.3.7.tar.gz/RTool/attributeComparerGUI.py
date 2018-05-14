import os
from functools import partial
import maya.cmds as mc

class attributeComparerWindow:

    def __init__(self):
        self.dictionaries = [0] * 2
        self.texts = []
        self.nodeTextField = None
        
        win = mc.window(title = "Attribute Checker")#, wh=(158,512))

        col = mc.columnLayout(adjustableColumn=True)
        self.defaultNodeTextFieldText = "Node Name"
        self.nodeTextField = mc.textField(
            alwaysInvokeEnterCommandOnReturn=True,
            text=self.defaultNodeTextFieldText)
        mc.rowLayout(numberOfColumns=2, columnAlign=[(1, "center"),(2,"center")])
        mc.columnLayout()
        #partialSetMatrix = partial(self.setMatrix, self.dictionaries)
        #1def partialSetMatrix(num):
          #  print("test: ", num)
           # self.setMatrix(self.dictionaries, num)
        mc.button(
            label="Set Original",
            command=partial(self.setMatrix, self.dictionaries, 0))#"partialSetMatrix(0)")#lambda self, dictionaries: #
                #self.setMatrix(dictionaries, 0))
        self.texts.append(mc.text(label="Set: No", align="center"))
        mc.setParent("..")
        mc.columnLayout()
        mc.button(
            label="Set Changed",
            command=partial(self.setMatrix, self.dictionaries, 1))#"partialSetMatrix(1)")#partial(self.setMatrix, self.dictionaries))#lambda self, dictionaries:
                #self.setMatrix(dictionaries, 1))
        self.texts.append(mc.text(label="Set: No", align="center"))
        mc.setParent("..")
        mc.setParent("..")
        mc.separator()
        self.readyText = mc.text(label="Is Ready: No", align="center")
        mc.button(
            label="Compare Changes",
            command=partial(self.refCompareChanges))

        mc.showWindow(win)

    def setMatrix(self, dictionaries, num, *args):
        nodeText = mc.textField(self.nodeTextField, query=True, text=True)
        print(nodeText)
        #print(mc.listAttr(nodeText))
        tempDictionary = {}
        if nodeText != self.defaultNodeTextFieldText:
            for i in mc.listAttr(nodeText):
                #print(i)
                try:
                    tempDictionary[i] = (
                        mc.getAttr("%s.%s"%(nodeText, i), silent=True, asString=True), 
                        mc.getAttr("%s.%s"%(nodeText, i), silent=True, asString=True, type=True),
                        mc.getAttr("%s.%s"%(nodeText, i), silent=True))
                except (RuntimeError, ValueError, TypeError) as e:
                    tempDictionary[i] = ("FAILED","NONE","FAILED")
            #print(tempDictionary)        
            
            self.dictionaries[num] = tempDictionary
            mc.text(self.texts[num], edit=True, label="Set: Yes")
            
            if self.dictionaries[0] != 0 and self.dictionaries[1] != 0:
                mc.text(self.readyText, edit=True, label="Is Ready: Yes")
                
    def refCompareChanges(self, *args):
        compareChanges(self.dictionaries)
        
class compareChanges():

    titles = ["Attribute Name","Original Value","Changed Value","Value Type","Get Real Value"]
    commands = [
        "key", 
        "self.dictionaries[0][key][0]", 
        "self.dictionaries[1][key][0]", 
        "self.dictionaries[1][key][1]"]
    comparisons = {}
        
    def __init__(self, dictionaries):
        self.dictionaries = dictionaries
        
        win = mc.window(title="Attribute Comparison", resizeToFitChildren=True)
        columns = len(self.titles)
        mc.columnLayout(adj=True)
        #mc.frameLayout(label="String values", collapsable=True)
        mc.scrollLayout()
        col = mc.rowLayout(numberOfColumns=columns)
        for i in range(columns):
            self.createColumn(i)
        #mc.frameLayout(label="Real values", collapsable=True)
    
        # Can add a list of only changed items

        mc.showWindow(win)
        
    def informationWindow(self, key, *args):
        win = mc.window(title="Attribute Information")
        mc.columnLayout(adj=1)
        mc.rowLayout(numberOfColumns=1)
        exec("name="+self.commands[0]) in locals(), globals()
        exec("oValue="+self.commands[1]) in locals(), globals()
        print(key)
        mc.columnLayout()
        mc.textFieldGrp(label="Name", text=name, enable=True)
        '''
        mc.columnLayout()
        mc.text(label="Name")
        mc.text(label="Original Value")
        mc.setParent("..")
        mc.columnLayout()
        mc.text(label=name, backgroundColor=[0,0,0])
        mc.text(label=oValue, backgroundColor=[0,0,0])
        '''
        exec("nameType="+self.commands[1]) in locals(), globals()
        #print(type)
        mc.textFieldGrp(label="Type", text=nameType, enable=False)#self.dictionaries[1][key][1]
        
        mc.showWindow(win)
        
    def handleCommand(self, i):
        keys = self.dictionaries[0].keys()
        for key in keys:
            if i != 4:
                check = False
                exec("tempString = str(%s)"%self.commands[i]) in locals(), globals()
                if i == 1:
                    self.comparisons[key] = tempString
                elif i == 2:
                    if self.comparisons[key] != tempString:
                        check = True
                tempText = mc.text(label=tempString[:35], height=15)  
                if check:
                    mc.text(
                        tempText,
                        edit=True,
                        font="boldLabelFont",
                        backgroundColor=(1,0.5,0.5))
            else:
                mc.button(
                    label="Real Value",
                    height=15,
                    command=partial(
                        self.informationWindow,
                        key))#lambda key : self.informationWindow(key))#informationWindow(key)")#"print(%s)"%dictionaries[1][key][2], height=15)
        
    def createColumn(self, i):
        mc.columnLayout()
        mc.text(label=self.titles[i], font="boldLabelFont")
        mc.separator(height=5, style="in")
        self.handleCommand(i)
        mc.setParent("..")

#def attributeComparerGUI():
#    attributeComparerWindow()
# see below for bit more modular version

def main():
    attributeComparerWindow()

if __name__ == "__main__":
    main()
else:
    exec("def %s():\n\tmain()"
        %os.path.basename(__file__).split('.')[0])
            

    
    
    
