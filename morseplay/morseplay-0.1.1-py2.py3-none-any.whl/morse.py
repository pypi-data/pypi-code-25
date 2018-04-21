import morse_talk as mtalk
import RPi.GPIO as GPIO
import time
from threading import Thread

class OutputMorse:
    def __init__(self, outpin, delay_unit=0.3, setmode=GPIO.BCM, warnings=False):
        GPIO.setmode(setmode)
        GPIO.setwarnings(warnings)
        GPIO.setup(outpin, GPIO.OUT)

        self.outpin = outpin
        self.delay_unit = delay_unit

    def send(self, data, morse=False, threaded=False):
        if not morse:
            data = mtalk.encode(data)
        if threaded:
            send_morse_bg = Thread(target=self._out, args=(data,))
            return send_morse_bg
        else:
            self._out(data)

    def _out(self, text):
        for code in text:
            if code in ('-', '.'):
                self._outcode(code)
            else:
                time.sleep(self.delay_unit*2)

    def _outcode(self, code):
        GPIO.output(self.outpin, GPIO.HIGH)

        if code == '.':
            time.sleep(self.delay_unit)
        elif code == '-':
            time.sleep(self.delay_unit*3)

        GPIO.output(self.outpin, GPIO.LOW)
        time.sleep(self.delay_unit)
