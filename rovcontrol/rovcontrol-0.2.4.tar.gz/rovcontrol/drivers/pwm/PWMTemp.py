import rovcontrol.drivers.DriverTemp as DriverTemp

class PWMTemp(DriverTemp.DriverTemp):
    default_bus_settings = {'freq' : 60, 'dirty' : True, 'channels' : {}}
    default_channel_settings = {'polarity' : 0, 'duty' : 0.0, 'dirty' : True}

    def __init__(self):
        self.reglist = [
            {'name' : "freq", 'type' : int, 'depth' : 1,
             'set' : self.set_freq, 'get' : self.get_freq},
            {'name' : "polarity", 'type' : int, 'depth' : 2,
             'set' : self.set_polarity, 'get' : self.get_polarity},
            {'name' : "duty", 'type' : float, 'depth' : 2,
             'set' : self.set_duty, 'get' : self.get_duty}]
        self.settings = {}
    def __str__(self):
        return str(self.settings)

    def enable_bus(self, bus):
        self.settings.update({bus : dict(self.default_bus_settings)})
        self.update()
    def enable_chan(self, bus, channel):
        self.settings[bus]['channels'].update({channel : dict(self.default_channel_settings)})
        self.update()

    def update(self):
        for i in self.settings.keys():
            self.update_one_bus(i, self.settings[i])

    def update_one_bus(self, bus, data):
        data['dirty'] = False
        for i in self.settings[bus]['channels'].keys():
            self.update_one_channel(bus, i, self.settings[bus]['channels'][i])

    def update_one_channel(self, bus, channel, data):
        data['dirty'] = False

    def set_freq(self, bus, freq):
        bus = int(bus)
        self.settings[bus]['freq'] = freq
        self.settings[bus]['dirty'] = True
        self.update()
    def set_polarity(self, bus, channel, polarity):
        bus = int(bus)
        channel = int(channel)
        self.settings[bus]['channels'][channel]['polarity'] = polarity
        self.settings[bus]['channels'][channel]['dirty'] = True
        self.update()
    def set_duty(self, bus, channel, duty):
        bus = int(bus)
        channel = int(channel)
        self.settings[bus]['channels'][channel]['duty'] = duty
        self.settings[bus]['channels'][channel]['dirty'] = True
        self.update()
