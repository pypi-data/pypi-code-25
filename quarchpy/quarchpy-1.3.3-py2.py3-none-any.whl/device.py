import time

from connection import QISConnection, PYConnection

class quarchDevice:
    
    def __init__(self, ConString, ConType = "PY"):
        self.ConString = ConString
        self.ConType = ConType

        # Initializes the object as a python or QIS connection
        ## Python
        if self.ConType == "PY":
            self.connectionObj = PYConnection(self.ConString)    # Creates the connection object. 
            
            # Exposes the connection type and module for later use.
            self.connectionName = self.connectionObj.ConnTarget
            self.connectionTypeName = self.connectionObj.ConnTypeStr
        
        ## QIS
        # ConType may be QIS only or QIS:ip:port [:3] checks if the first 3 letters are QIS.
        elif self.ConType[:3] == "QIS":
            # If host and port are specified.
            try:
                # Extract QIS, host and port.
                QIS, host, port = self.ConType.split(':')
                # QIS port should be an int.
                port = int(port)
            # If host and port are not specified. 
            except:
                host='127.0.0.1'
                port=9722

            # Creates the connection object.
            self.connectionObj = QISConnection(self.ConString, host, port)  
                        
        ## Neither PY or QIS, connection cannot be created.
        else:
            raise ValueError("Invalid connection type. Please select PY or QIS")
  
    def sendCommand(self, CommandString):
        if self.ConType[:3] == "QIS":
            return self.connectionObj.qis.sendCmd(self.ConString.replace(':', '::'), CommandString)
        else:
            return self.connectionObj.connection.sendCommand(CommandString)

    def openConnection(self):
        if self.ConType[:3] == "QIS":
            self.connectionObj.qis.connect()
            return "OK"
        else:
            del self.connectionObj
            self.connectionObj = PYConnection(self.ConString)
            return self.connectionObj

    def closeConnection(self):
        if self.ConType[:3] == "QIS":
            self.connectionObj.qis.disconnect()
            return "OK"
        else:
            self.connectionObj.connection.close()
            return "OK"