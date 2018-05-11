import rovcontrol.drivers.motor.MotorTemp as MotorTemp
import rovcontrol.drivers.abstract.PWMBlock as PWMBlock
import RPi.GPIO as GPIO #TODO: abstract away gpio

class Pololu18v17(MotorTemp.MotorTemp):
    MAX_PWM = 0.98
    MIN_PWM = 0
    def __init__(self, pwml, dirl, sleepl):
        pwml.set_freq(20000)
        GPIO.setmode(GPIO.BCM)
        super().__init__(range(0, pwml.len() - 1))

    def update_one_channel(self, channel, data):
        if data['dirty']:
            GPIO.output(sleepl[channel], not data['sleep'])
            pwml.set_duty(channel, data['speed'] / 100.0 * (MAX_PWM - MIN_PWM) + MIN_PWM)
            GPIO.output(dirl[channel], data['dir'])
            if data['brake']:
                pwml.set_duty(channel, 0)
        super()
