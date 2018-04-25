from device import quarchDevice

class quarchBreakerDevice(quarchDevice):
    def __init__(self, originObj):
        self.connectionObj = originObj.connectionObj
        self.ConString = originObj.ConString
        self.ConType = originObj.ConType
 
    def SetupHotSwapBySpeed(self, stepTime):
        return "\n\n(not) starting Hot Swap with " + str(stepTime) + "ms step. \n\n"