#!/usr/bin/python3
from PIL import Image, ImageTk

from statistics import Statistics
from statisticGUI import StatisticGUI

import tkinter as tk
from tkinter import ttk

from tkinter import font
from tkinter import StringVar
from tkinter import Button, Frame, Grid, Label
from tkinter import FLAT, LEFT, RAISED, SUNKEN, TOP
from tkinter import E, N, S, X, W

class Toolbar(tk.Frame):
    """ Toolbar """
    def onQuit(self):        
        self.root.gameFrame.onQuit()

    def onNewGame(self):
        self.root.gameFrame.onNewGame()

    def onStatistics(self):
        statistics = Statistics()
        dialog = StatisticGUI(self.root, statistics.getStatistics())
        self.root.wait_window(dialog.top)
        
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        maxsize = (32, 32)
        exitPng = Image.open(r".\Icons\log-out-icon.png")
        exitPng.thumbnail(maxsize, Image.ANTIALIAS)
        exitImage = ImageTk.PhotoImage(exitPng)
        exitButton = Button(self, image=exitImage, relief=FLAT, command=self.onQuit)
        exitButton.image = exitImage
        exitButton.grid(row=0, column=1, sticky='w', padx=2, pady=2)

        newPng = Image.open(r".\Icons\new-icon.png")
        newPng.thumbnail(maxsize, Image.ANTIALIAS)
        newImage = ImageTk.PhotoImage(newPng)
        newButton = Button(self, image=newImage, relief=FLAT, command=self.onNewGame)
        newButton.image = newImage
        newButton.grid(row=0, column=2, sticky='w', padx=2, pady=2)

        statisticsPng = Image.open(r".\Icons\chart-icon.png")
        statisticsPng.thumbnail(maxsize, Image.ANTIALIAS)
        statisticsImage = ImageTk.PhotoImage(statisticsPng)  
        statisticsButton = Button(self, image=statisticsImage, relief=FLAT, command=self.onStatistics)
        statisticsButton.image = statisticsImage
        statisticsButton.grid(row=0, column=3, sticky='w', padx=2, pady=2)

        self.pack(side=tk.TOP, fill=tk.X)
 