import tkinter

if '__tk_inited' not in globals():
    global __tk_inited
    __tk_inited = False

def init():
    global __tk_inited
    if not __tk_inited:
        w = tkinter.Tk()
        w.withdraw()
    
def setInited():
    global __tk_inited
    __tk_inited = True
