import rovcontrol.drivers.adc.ADCTemp as ADCTemp

class ADCBlock:
    def __init__(self):
        self.settings = {}
    def __str__(self):
        return str(self.settings)

    def map_chan(self, controller, real_bus, real_chan, logical_chan):
        self.settings.update({logical_chan : {'controller' : controller, 'real_bus' : real_bus, 'real_chan' : real_chan}})

    def set_vref(self, vref):
        for i in self.settings.keys():
            self.settings[i]['controller'].set_vref(self.settings[i]['real_bus'], vref)
    def get_vref(self):
        for i in self.settings.keys():
            self.settings[i]['controller'].get_vref(self.settings[i]['real_bus'])
        return 0

    def set_mv(self, logical_chan, mv):
        self.settings[logical_chan]['controller'].set_mv(
            self.settings[logical_chan]['real_bus'], self.settings[logical_chan]['real_chan'], mv)
    def get_mv(self, logical_chan):
        return self.settings[logical_chan]['controller'].get_mv(
            self.settings[logical_chan]['real_bus'], self.settings[logical_chan]['real_chan'])
