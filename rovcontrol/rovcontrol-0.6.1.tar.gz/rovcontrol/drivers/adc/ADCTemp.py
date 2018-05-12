import rovcontrol.drivers.DriverTemp as DriverTemp
import copy

class ADCTemp(DriverTemp.DriverTemp):
    default_bus_settings = {'vref' : 0, 'dirty' : True, 'channels' : {}}
    default_channel_settings = {'mv' : 0, 'dirty' : True}

    def __init__(self):
        self.reglist = []
        self.settings = {}
    def __str__(self):
        return str(self.settings)

    def enable_bus(self, bus):
        self.settings.update({bus : copy.deepcopy(self.default_bus_settings)})
        self.update()
    def enable_chan(self, bus, channel):
        self.settings[bus]['channels'].update({channel : copy.deepcopy(self.default_channel_settings)})
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

    def set_vref(self, bus, vref):
        bus = int(bus)
        self.settings[bus]['vref'] = vref
        self.settings[bus]['dirty'] = True
        self.update()
    def get_vref(self, bus):
        bus = int(bus)
        return self.settings[bus]['vref']

    def set_mv(self, bus, channel, mv):
        pass
    def get_mv(self, bus, channel):
        bus = int(bus)
        channel = int(channel)
        self.settings[bus]['channels'][channel]['dirty'] = True
        self.update()
        return self.settings[bus]['channels'][channel]['mv']
