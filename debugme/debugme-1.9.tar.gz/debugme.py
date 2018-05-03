import code
import inspect
import readline
import rlcompleter
import sys
import traceback
from pprint import pprint

def displayhook(value):
    pprint(value)
    if isinstance(__builtins__, dict):
        __builtins__['_'] = value
    else:
        __builtins__._ = value

class formatted_repr(str):
    def __repr__(self):
        return self

class debugme:
    def __init__(self, frame, exc_info):
        self.frame = frame
        self.exc_info = exc_info
        self.exit = True
        self.traceback = formatted_repr(''.join(traceback.format_stack(self.frame)).strip())

    def __del__(self):
        del(self.frame)

    @property
    def back(self):
        frame = self.frame.f_back
        if not frame:
            sys.stderr.write("No frame to go back to\n")
            return
        run(frame, None)

def auto_run():
    sys.displayhook = displayhook
    frame = inspect.currentframe()
    exc_info = None
    while True:
        module = inspect.getmodule(frame)
        in_importlib = not module and 'importlib' in frame.f_code.co_filename
        if not in_importlib and (not module or module.__name__ != 'debugme'):
            if frame.f_code == sys.excepthook.__code__:
                exc_info = [frame.f_locals[x] for x in frame.f_code.co_varnames[:frame.f_code.co_argcount]]
                tb = exc_info[2]
                while tb.tb_next:
                    tb = tb.tb_next
                frame = tb.tb_frame
            break
        frame_, frame = frame, frame.f_back
        del(frame_)
    run(frame, exc_info)

def run(frame, exc_info):
    vars = frame.f_globals
    vars.update(frame.f_locals)
    vars['debugme'] = debugme(frame, exc_info)
    del(frame)

    readline.set_completer(rlcompleter.Completer(vars).complete)
    readline.parse_and_bind("tab: complete")
    shell = code.InteractiveConsole(vars)
    shell.interact()
    if vars['debugme'].exit:
        sys.exit(1)

auto_run()
