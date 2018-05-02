from device import quarchDevice

class quarchPPM(quarchDevice):
    def __init__(self, originObj):
        self.connectionObj = originObj.connectionObj
        self.ConString = originObj.ConString
        self.ConType = originObj.ConType
 
    def startStream(self, fileName='streamData.txt', fileMaxMB=2000, streamName='Stream With No Name', streamAverage = None):
        return self.connectionObj.qis.startStream(self.ConString.replace(':', '::'), fileName, fileMaxMB, streamName, streamAverage)

    def streamRunningStatus(self):
        return self.connectionObj.qis.streamRunningStatus(self.ConString.replace(':', '::'))

    def streamBufferStatus(self):
        return self.connectionObj.qis.streamBufferStatus(self.ConString.replace(':', '::'))

    def streamInterrupt(self):
        return self.connectionObj.qis.streamInterrupt()

    def streamingStopped(self):
        return self.connectionObj.qis.streamingStopped()

    def stopStream(self):
        return self.connectionObj.qis.stopStream(self.ConString.replace(':', '::'))

