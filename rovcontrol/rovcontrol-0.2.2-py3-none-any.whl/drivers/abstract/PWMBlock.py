import rovcontrol.drivers.pwm.PWMTemp as PWMTemp

class PWMBlock:
    def __init__(self):
        self.settings = {}
    def __str__(self):
        return str(self.settings)

    def map_chan(self, controller, real_bus, real_chan, logical_chan):
        self.settings.update({logical_chan : {'controller' : controller, 'real_bus' : real_bus, 'real_chan' : real_chan}})

    def set_freq(self, freq):
        for i in self.settings.keys():
            self.settings[i]['controller'].set_freq(self.settings[i]['real_chan'], freq)
    def set_polarity(self, logical_chan, polarity):
        settings[logical_chan]['controller'].set_polarity(
            settings[logical_chan]['real_bus'], settings[logical_chan]['real_chan'], polarity)
    def set_duty(self, logical_chan, duty):
        settings[logical_chan]['controller'].set_polarity(
            settings[logical_chan]['real_bus'], settings[logical_chan]['real_chan'], duty)
