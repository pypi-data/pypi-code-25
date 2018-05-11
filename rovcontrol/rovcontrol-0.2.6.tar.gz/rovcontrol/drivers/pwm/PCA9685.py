import rovcontrol.drivers.pwm.PWMTemp as PWMTemp
import Adafruit_PCA9685

#TODO: implement polarity

class PCA9685(PWMTemp.PWMTemp):
    def __init__(self, i2caddress = 0x40, i2cbus = 1):
        super().__init__()
        self.adapwm = Adafruit_PCA9685.PCA9685(address = i2caddress, busnum = i2cbus)

    def update_one_bus(self, bus, data):
        if data['dirty']:
            self.adapwm.set_pwm_freq(data['freq'])
        super()

    def update_one_channel(self, bus, channel, data):
        if data['dirty']:
            self.adapwm.set_pwm(channel, 0, data['duty'] * 4096)
        super()
