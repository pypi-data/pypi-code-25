import pprint
from subprocess import *
from pathlib import Path
from abc import ABC, abstractmethod
from collections import namedtuple
import pickle, os
import hashlib
from IPython.core.magic import *
from .util import *
        
class CheckpointHandler(ABC):
    @abstractmethod
    def checkpoint(self, ipython, name, value):
        pass

    @abstractmethod        
    def restore(self, ipython, name, metadata):
        pass

    @classmethod
    def path_of(cls, name):
        m = hashlib.sha256()
        m.update(name.encode("utf-8"))
        os.makedirs(".cache", exist_ok = True)
        return Path(".cache") / m.hexdigest()

class PathHandler(CheckpointHandler):
    
    def checkpoint(self, ipython, name, value):
        print(value)
        if Path(str(value)).is_file():
            link_f(Path(str(value)), self.path_of(name))
            return str(value)
        else:
            return None
            
    def restore(self, ipython, name, metadata):
        if Path(metadata).is_file():
            print("not overwriting existing file: "+metadata)
        else:
            os.link(self.path_of(name), metadata)
    
class PickleHandler(CheckpointHandler):
    def checkpoint(self, ipython, name, value):
        with open(self.path_of(name), "wb") as file:
            pickle.dump(value, file)
        return True
     
    def restore(self, ipython, name, metadata):
        with open(self.path_of(name), "rb") as file:
            ipython.user_ns[name] = pickle.load(file)

@magics_class
class CheckpointMagics(Magics):
    def __init__(self, handlers = [PathHandler(), PickleHandler()], **kwargs):
        super(CheckpointMagics, self).__init__(**kwargs)
        self.enabled = False
        self.handlers = handlers
        
    def save(self, name):
        value = self.shell.user_ns[name]
        for handler in self.handlers:
            metadata = handler.checkpoint(self.shell, name, value)
            if metadata:
                all = (type(handler), metadata)
                with open(handler.path_of(name).with_suffix(".metadata"), 'wb') as file:
                    pickle.dump(all, file)
                return

    @line_magic
    def uncache(self, line, cell = None):
        name = line.strip()
        unlink_f(handler.path_of(name))
        unlink_f(handler.path_of(name).with_suffix(".metadata"))
    
    @line_cell_magic
    def recache(self, line, cell = None):
        self.cache(line, cell, overwrite = True)
        
    @line_cell_magic
    def cache(self, line, cell = None, overwrite = False):
        name = line.strip()
        if cell:            
            if self.enabled:
                metadata_path = CheckpointHandler.path_of(name).with_suffix(".metadata")
                if metadata_path.is_file() and not overwrite:
                    print("loading from cache")
                    with open(metadata_path, 'rb') as file:
                        metadata = pickle.load(file)
                        cls = metadata[0]
                        for handler in self.handlers:
                            if type(handler) == cls:
                                handler.restore(self.shell, name, metadata[1])
                                return
                else:
                    self.shell.run_cell(cell)
                    self.save(name)
            else:
                self.shell.run_cell(cell)
        else:
            self.save(name)

    @line_magic
    def caching(self, line):
        line = line.strip()
        if line == "on":
            self.enabled = True
        elif line == "off":
            self.enabled = False
