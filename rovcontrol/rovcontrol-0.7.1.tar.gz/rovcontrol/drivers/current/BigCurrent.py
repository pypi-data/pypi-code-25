import rovcontrol.drivers.current.CurrentTemp as CurrentTemp
import rovcontrol.drivers.abstract.ADCBlock as ADCBlock

class BigCurrent(CurrentTemp.CurrentTemp):
    VREF = 5000
    def __init__(self, channels, adcl):
        adcl.set_vref(self.VREF)
        self.adcl = adcl
        super().__init__(channels)

    def scale(self, value):
        return (value - self.VREF / 2) / 20.0

    def update_one_channel(self, channel, data):
        if data['dirty']:
            data['current'] = self.scale(self.adcl.get_mv(channel))
        super().update_one_channel(channel, data)
