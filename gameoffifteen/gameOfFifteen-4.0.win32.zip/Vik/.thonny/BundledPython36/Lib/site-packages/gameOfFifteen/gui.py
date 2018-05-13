#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
import toolbar
from toolbar import Toolbar
import gameframe
from gameframe import GameFrame
import statusbar
from statusbar import StatusBar

from statistics import Statistics

class Gui(tk.Frame):
    """ main class for the application """
    def __init__(self, root, *args, **kwargs):
        super().__init__(root,*args,**kwargs)
        root.title('15er-Puzzle')        
        self.toolBar = Toolbar(self) 
        self.statusBar = StatusBar(self)
        self.gameFrame = GameFrame(self)
        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        root.configure(bg = 'black', padx=2, pady=2)
        self.center(root)
        statistics = Statistics()

    def center(self, toplevel):
        toplevel.update_idletasks()
        screenWidth = toplevel.winfo_screenwidth()
        screenHeight = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = screenWidth/2 - size[0]/2
        y = screenHeight/2 - size[1]/2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

if __name__ == "__main__": 
    root = tk.Tk() 
    gui = Gui(root) 
    root.mainloop()
