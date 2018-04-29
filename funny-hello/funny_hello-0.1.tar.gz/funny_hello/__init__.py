# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 12:17:23 2018

@author: amir.rahmani
"""

# Define a function
def world():
    print("Hello, World!")

# Define a variable
shark = "Sammy"


# Define a class
class Octopus:
    def __init__(self, name, color):
        self.color = color
        self.name = name

    def tell_me_about_the_octopus(self):
        print("This octopus is " + self.color + ".")
        print(self.name + " is the octopus's name.")