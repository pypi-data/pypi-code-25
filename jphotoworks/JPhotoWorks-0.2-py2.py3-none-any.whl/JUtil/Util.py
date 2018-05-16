import os
import errno

class Util(object):
    def __init__(self):
        self.className = 'Util'

    def getAbsPath(self, filename):
        absPath =  os.path.abspath(filename) # This is your Project Root
        return absPath

    def makeDir(self, path):
        if os.path.isfile(path) :
            directory = os.path.dirname(path)
        else :
            directory = path
        if not os.path.exists(directory):
            os.makedirs(directory)