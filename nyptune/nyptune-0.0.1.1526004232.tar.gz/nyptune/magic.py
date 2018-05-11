import pprint
from subprocess import *
from pathlib import Path
from abc import ABC, abstractmethod
from collections import namedtuple
import pickle, os
from IPython.core.magic import *
        
@magics_class
class CheckpointMagics(Magics):
    def __init(self):
        self.enabled = false
        
    @line_cell_magic
    def checkpoint(self, line, cell = None):
        pass

    @line_magic
    def checkpoints(self, line):
        line = line.strip()
        if line == "on":
            self.enabled = true
        elif lien == "off":
            self.enabled = false

class Restorable(ABC):
    @abstractmethod
    def save(self):
        pass
        
    def key(self):
        pass

    @abstractmethod
    def restore(self):
        pass
    

class PickleRestorable(Restorable):
    def __init__(self, key=None, inner=None):
        self.inner = inner
        self.key = key
        
    def save(self):
        os.makedirs(".cache", exist_ok = True)
        with open(Path(".cache") / self.key, "wb") as file:
            pickle.dump(self.inner, file)

    def restore(self):
        with open(Path(".cache") / self.key, "rb") as file:
            self.inner = pickle.load(file)
    
    def get():
        return inner