#!/usr/bin/python3

import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from tkinter import Label
from tkinter import FLAT

import statistics
from statistics import Statistics

class StatusBar(tk.Frame):
    """ Simple Status Bar class - based on Frame """
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.master = root

        self.timeUsedInSecs = 0
        self.countOfMoves = 0
        self.countOfMoveButtons = 0
        self.currentMoves = StringVar()
        self.currentMoves.set(self.updateCurrentMoves())
        self.movesLabel = Label(self, relief=FLAT, textvariable=self.currentMoves)
        self.movesLabel.pack()
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def updateCurrentMoves(self):
        usedTime = Statistics.formatDuration(self.timeUsedInSecs)
        self.currentMoves.set(str("{}Züge - {}Knöpfe Spielzeit {}".format(self.countOfMoves, self.countOfMoveButtons, usedTime)))

    def set(self, moves, moveButtons, timeUsedInSecs):
        self.countOfMoves = moves
        self.countOfMoveButtons = moveButtons
        self.timeUsedInSecs = timeUsedInSecs 
        self.updateCurrentMoves()
        self.movesLabel.update_idletasks()


    def clear(self):
        self.countOfMoves = 0
        self.countOfMoveButtons = 0
        self.updateCurrentMoves()
        self.movesLabel.update_idletasks()

