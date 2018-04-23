#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
import sys

import betterdialogs as bd


class MainWindow(bd.MainFrame):
    def content(self, master):
        self.string = tk.StringVar()
        self.entry = ttk.Entry(master, textvariable=self.string)
        self.entry.pack(padx=2, pady=2, fill="x")

        ttk.Button(
            master,
            text="Pad and copy",
            command=self.on_click
        ).pack(padx=2, pady=2, fill="x")

        self.entry.bind("<Return>", self.bind_on_click)

        self.entry.focus_set()

    def bind_on_click(self, event):
        self.on_click()

    def on_click(self):
        text = self.string.get().strip()
        self.string.set("")

        if len(text) % 2:
            text = text + " "
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        self.parent.update()


def main():
    root = tk.Tk()
    if "-L" in sys.argv:
        root.tk.call("tk", "scaling", 0.6)
    MainWindow(root, "EcoPad - Pad your chat.")

if __name__=="__main__":
    main()
