import rovcontrol.drivers.DriverTemp as DriverTemp
import copy

class CurrentTemp(DriverTemp.DriverTemp):
    default_channel_settings = {'current' : 0, 'dirty' : True}

    def __init__(self, channels):
        self.settings = {}
        self.reglist = [
            {'name' : "current", type : int, 'depth' : 1,
             'set' : self.set_current, 'get' : self.get_current}]
        for i in channels:
            self.settings.update({i : copy.deepcopy(self.default_channel_settings)})
        self.update()
    def __str__(self):
        return str(self.settings)

    def update(self):
        for i in self.settings.keys():
            self.update_one_channel(i, self.settings[i])

    def update_one_channel(self, channel, data):
        data['dirty'] = False

    def set_current(self, channel, current):
        pass
    def get_current(self, channel):
        channel = int(channel)
        self.settings[channel]['dirty'] = True
        self.update()
        return self.settings[channel]['current']
