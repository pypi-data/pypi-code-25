import os, sys
import inspect
import time 


def startLocalQIS():
    current_direc = os.getcwd()
    os.chdir(os.path.abspath(__file__) + "\\..\\connection_specific\\QIS\\")
    
    startQISchar = "start /b java -Djava.awt.headless=true -jar " + os.path.abspath(__file__) + "\\..\\connection_specific\\QIS\\qis.jar > pipe"
    os.system(startQISchar)
    time.sleep(3)

    os.chdir(current_direc)

    startLocalQIS.func_code = (lambda:None).func_code 
    
class QISConnection:
    
    def __init__(self, ConString, host, port):
        
        from connection_QIS import QisInterface
        self.qis = QisInterface(host, port) 	# Create an instance of QisInterface. Before this is ran QIS needs to have been started
        
class PYConnection:
    
    def __init__(self, ConString):
        # Finds the separator.
        Pos = ConString.find (':')
        if Pos is -1:
            raise ValueError ('Please check your module name!')
        # Get the connection type and target.
        self.ConnTypeStr = ConString[0:Pos]
        self.ConnTarget = ConString[(Pos+1):]
        
        if self.ConnTypeStr.lower() == 'rest':
            from connection_ReST import ReSTConn
            self.connection = ReSTConn(self.ConnTarget)
            
        elif self.ConnTypeStr.lower() == 'usb':
            from connection_USB import USBConn
            self.connection = USBConn(self.ConnTarget)
        
        elif self.ConnTypeStr.lower() == 'serial':
            from connection_Serial import SerialConn
            self.connection = SerialConn(self.ConnTarget)
        
        elif self.ConnTypeStr.lower() == 'telnet':
            from connection_Telnet import TelnetConn
            self.connection = TelnetConn(self.ConnTarget)
        
        else:
            return "Please check your connection string."
