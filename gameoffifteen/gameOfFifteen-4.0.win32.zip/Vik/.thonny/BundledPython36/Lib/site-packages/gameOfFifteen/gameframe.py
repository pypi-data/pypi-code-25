#!/usr/bin/python3

from PIL import Image, ImageTk

import datetime 
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from tkinter import StringVar
from tkinter import Button, Frame, Grid, Label
from tkinter import BOTTOM, FLAT, LEFT, RAISED, RIGHT, SUNKEN, TOP
from tkinter import E, N, S, X, W

import businessLogic
from businessLogic import BusinessLogic
import statistics
from statistics import Statistics

class GameFrame(tk.Frame):
    """The sort buttons gui and functions."""

    redNumbers = [1, 3, 6, 8, 9, 11, 14]
    whiteNumbers = [2, 4, 5, 7, 10, 12, 13, 15]
    
    def __init__(self, root, *args, **kwargs):
        """Constructor."""
        super().__init__(root, *args, **kwargs)
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        self.businessLogic = BusinessLogic()
        self.statistic = Statistics()
        self.init_gui()
        self.pack(side=BOTTOM, fill=X)

    def init_gui(self):
        """Builds GUI."""
        for columnIndex in range(0, self.businessLogic.ColumnCount):
            Grid.columnconfigure(self, columnIndex, weight=1)
        for rowIndex in range(0, self.businessLogic.RowCount):
            Grid.rowconfigure(self, rowIndex, weight=1)
        self.configure(bg = 'black', padx=2, pady=2)
        self.prepareNewGame()

    def on_enter(self, event):
        """Handles a button mouse enter event."""
        moveCount = self.root.statusBar.countOfMoves
        moveCountButton = self.root.statusBar.countOfMoveButtons        
        button = event.widget
        buttonNumber = int(button["text"])
        if self.businessLogic.isMovePossible(buttonNumber):
            moveCount = moveCount + 1
            selectedRow = self.businessLogic.rowOfValue(buttonNumber)
            selectedColumn = self.businessLogic.columnOfValue(buttonNumber)
            holeRow = self.businessLogic.rowOfValue(0)
            holeColumn = self.businessLogic.columnOfValue(0)
            
            selectionButton = self.findInGrid(self, selectedColumn, selectedRow)
            hole = self.findInGrid(self, holeColumn, holeRow) 

            if selectedRow == holeRow:
                # move horizontal
                if selectedColumn < holeColumn:
                    # move all to the right
                    while selectedColumn < holeColumn:
                        moveCountButton = moveCountButton + 1
                        button = self.findInGrid(self, holeColumn - 1, holeRow)                        
                        button.grid(column=holeColumn, row=holeRow)
                        self.businessLogic.MoveToHole(holeColumn - 1, holeRow)
                        holeColumn = holeColumn - 1    
                else:
                    #move all to left
                    while selectedColumn > holeColumn:
                        moveCountButton = moveCountButton + 1                        
                        button = self.findInGrid(self, holeColumn + 1, holeRow)                        
                        button.grid(column=holeColumn, row=holeRow)
                        self.businessLogic.MoveToHole(holeColumn + 1, holeRow)
                        holeColumn = holeColumn + 1    
            else:
                # move vertical
                if selectedRow < holeRow:
                    # move all up
                    while selectedRow < holeRow:
                        moveCountButton = moveCountButton + 1 
                        button = self.findInGrid(self, holeColumn, holeRow - 1)                        
                        button.grid(column=holeColumn, row=holeRow)
                        self.businessLogic.MoveToHole(holeColumn, holeRow - 1)
                        holeRow = holeRow - 1    
                else:
                    #move all down
                    while selectedRow > holeRow:
                        moveCountButton = moveCountButton + 1
                        button = self.findInGrid(self, holeColumn, holeRow + 1)                        
                        button.grid(column=holeColumn, row=holeRow)
                        self.businessLogic.MoveToHole(holeColumn, holeRow + 1)
                        holeRow = holeRow + 1    

            usedGameTime = int((datetime.datetime.now() - self.startGameTime).total_seconds())
            self.root.statusBar.set(moveCount, moveCountButton, usedGameTime)
            solutionName = self.businessLogic.allSorted()
            if solutionName != None:
                self.statistic.add(solutionName, moveCount, moveCountButton, usedGameTime)
                messageBoxReturn = messagebox.askretrycancel(solutionName, "Play again", )
                if messageBoxReturn == False:
                    self.onQuit()
                else:
                    self.prepareNewGame()
            
    def prepareNewGame(self):        
        """Setup a new game."""
        self.startGameTime = datetime.datetime.now()
        self.root.statusBar.clear()
        buttonFont = font.Font(family='Helvetica', size=32, weight='bold')
        self.businessLogic.shuffle()
        for columnIndex in range(0, self.businessLogic.ColumnCount):
            for rowIndex in range(0, self.businessLogic.RowCount):
                button = self.findInGrid(self, columnIndex, rowIndex)
                if button is not None:
                    button.destroy()
                if self.businessLogic.valueAt(columnIndex, rowIndex) == 0:
                    continue
                else:
                    number = self.businessLogic.valueAt(columnIndex, rowIndex)
                    background = self.getBackgroundOf(number)
                    foreground = 'gold'
                    button = tk.Button(self, width=3, height=1, fg=foreground, bg=background, font=buttonFont,
                                       text=repr(self.businessLogic.valueAt(columnIndex, rowIndex)).rjust(2))
                    button.bind("<Enter>", self.on_enter)
                    button.grid(column=columnIndex, row=rowIndex)
                    
    def getBackgroundOf(self, number):
        if number in GameFrame.redNumbers:
            return 'red'
        if number in GameFrame.whiteNumbers:
            return 'white'
        return 'lightgrey'
    
    def onNewGame(self):
        """Prepare a new game."""
        self.prepareNewGame()
    
    def onStatistics(self):
        pass
    
    def onQuit(self):
        """Exits program."""
        quit()
    
    def updateCurrentMoves(self):
        self.currentMoves.set(str("{}Züge/{}Knöpfe".format(self.moves, self.moveKeys)))
     
    def findInGrid(self, frame, column, row):
        """Find a widget in the grid and returns it."""
        for child in frame.children.values():
            info = child.grid_info()
            try:            
                if info['row'] == row and info['column'] == column:
                    return child
            except:
                pass
        return None
     
