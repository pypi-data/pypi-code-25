#import threading

__version__ = "0.1.0"

import concurrent.futures
import sys

if sys.version[0] == '3':
    import tkinter as Tk
    import queue
else:
    import Tkinter as Tk
    import Queue as queue
import time

def main():

    root = Tk.Tk()

    # this thing handles the threading
    executor = concurrent.futures.ThreadPoolExecutor(8)

    ##############################################################

    # maxsize will halt threads putting more stuff on the queue until it's cleared
    # could potentially lock the program if a state is reached where the queue is full 
    # and nothing could take stuff of the queue.
    # we avoid this by making the main thread always take stuff off the queue
    q = queue.Queue(maxsize=1)

    def on_main_thread(func):
        q.put(func)

    def check_queue():
        while True:
            try:
                task = q.get(block=False)
                # if q is full it will raise queue.Empty
            except queue.Empty:
                break
            else:
                # execute task() when the gui is idle
                root.after_idle(task)
        root.after(10, check_queue)
        
    def handle_click_q():
        def callback():
            while not root.paused:
                root.running = True
                root.total += 1
                if root.total % 1 == 0:
                    root.on_main_thread(lambda: label1.config(text=str(root.total)+' ms'))
                    time.sleep(0.01) # gets the counter to update every ms
            if root.paused==True:
                root.running=False
                print('pausing!')
        if root.running:
            print('already running!')
        else:
            print('unpausing!')
            root.paused = False
            executor.submit(callback)        
        
    def handle_pause():
        def callback():
            root.paused = True
        executor.submit(callback)
        
    def handle_stop():
        # a stop is just a pause with a counter reset
        def callback():
            handle_pause()
            root.total = 0
            root.on_main_thread(lambda: label1.config(text=str(root.total)))
            print('resetting!')
        executor.submit(callback)
        
    #######################################################################

    root.running = False
    root.total = 0
    root.paused = False
    root.quit = False
    root.on_main_thread = on_main_thread
    root.check_queue = check_queue


    root.geometry('{}x{}'.format(640, 480))
    root.title("Alexei's Digital Stopwatch")
    label1 = Tk.Label(root, text='Please wait...')
    label1.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    button1 = Tk.Button(root, text='start', command=handle_click_q).pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    button2 = Tk.Button(root, text='stop', command=handle_stop).pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    button3 = Tk.Button(root, text='pause', command=handle_pause).pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    quit_button = Tk.Button(root, text='kill', command=root.destroy).pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    root.after(100, root.check_queue)
    root.mainloop()
