import os

from zc.buildout.testing import system
from zc.buildout.testrecipes import Debug

class Recipe(Debug):
    def __init__(self, buildout, name, options):
        self.options = options
        self.runvars()

    def runvars(self):
        print("interpretting runvar options")
        items = list(self.options.items())
        items.sort()
        for option, value in items:
            if value.startswith("`") and value.endswith("`"):
                cmd = value[1:-1]
                with os.popen(cmd) as p:
                    new_value = p.read().strip()
                #new_value = system(cmd)   # checkout system's with_exit_code=True for a good laugh
 
                self.options[option] = new_value
                print("  %s=%r  <--  %r" % (option, new_value, value))
            else:   
                print("  %s=%r" % (option, value))
        return ()
