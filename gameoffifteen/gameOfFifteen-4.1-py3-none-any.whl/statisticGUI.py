from tkinter import *
import tkinter

class StatisticGUI(Toplevel):

    def __init__(self, parent, items):
        top = self.top = Toplevel.__init__(self, parent)
        self.transient(parent)
        self.parent = parent
        self.result = None
        self.body = Frame(self)
        self.initial_focus = self.body
        self.winfo_toplevel().title("Statistik")
        
        Grid.columnconfigure(self, 0, weight=1, minsize=400)
        Grid.rowconfigure(self, 0, weight=1)
            
        self.e = Entry(top)        
        self.listbox = Listbox(self)
        self.listbox.grid(column=0, row=0, sticky='news')
        
        for item in items:
            self.listbox.insert(END, item)
        okButton = Button(self, text="OK", width=10, command=self.ok)
        okButton.grid(column=0, row=1)
        self.center(self)

    def center(self, toplevel):
        toplevel.update_idletasks()
        screenWidth = toplevel.winfo_screenwidth()
        screenHeight = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = screenWidth/2 - size[0]/2
        y = screenHeight/2 - size[1]/2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

    def ok(self):
        self.destroy()