import rovcontrol.drivers.motor.MotorTemp as MotorTemp
import rovcontrol.drivers.abstract.PWMBlock as PWMBlock
import RPi.GPIO as GPIO #TODO: abstract away gpio

class Pololu18v17(MotorTemp.MotorTemp):
    MAX_PWM = 0.9999
    MIN_PWM = 0
    def __init__(self, pwml, dirl, sleepl):
        pwml.set_freq(20000)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(dirl, GPIO.OUT)
        GPIO.setup(sleepl, GPIO.OUT)
        self.sleepl = sleepl
        self.dirl = dirl
        self.pwml = pwml
        super().__init__(range(0, len(dirl)))

    def update_one_channel(self, channel, data):
        if data['dirty']:
            GPIO.output(self.sleepl[channel], not data['sleep'])
            self.pwml.set_duty(channel, data['speed'] / 100.0 * (self.MAX_PWM - self.MIN_PWM) + self.MIN_PWM)
            GPIO.output(self.dirl[channel], data['dir'])
            if data['brake']:
                self.pwml.set_duty(channel, 0)
        super().update_one_channel(channel, data)
