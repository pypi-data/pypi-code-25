import time
import smbus2

class AnalogModule:
    adc_type = 'MCP4324'
    GAIN_MASK = 0x03
    CHANNEL_MASK = 0x60
    NOT_READY_MASK = 0x80
    RESOLUTION_MASK = 0x0C
    CONTINUOUS_MODE_MASK = 0x10

    R1 = 30100.0
    R2 = 120000.0
    VD = R1 / (R1 + R2)

    CHANNELS = {0: 0b0000000, 
                  1: 0b0100000, 
                  2: 0b1000000, 
                  3: 0b1100000
    }

    GAINS = {1: 0b00,
               2: 0b01,
               4: 0b10,
               8: 0b11
    }

    RESOLUTIONS = {12: 0b0000,
                     14: 0b0100,
                     16: 0b1000,
                     18: 0b1100
    }

    RESOLUTION_TO_DELAY = {12: 1.0/240,
                            14: 1.0/60,
                            16: 1.0/15,
                            18: 1.0/3.75
    }

    RESOLUTION_TO_LSB = {12: 1e-3,
                          14: 250e-6,
                          16: 62.5e-6,
                          18: 15.625e-6
    }


    def config_to_resolution(self):
        return [g for g, c in self.RESOLUTIONS.items() if c == self.config & self.RESOLUTION_MASK][0]

    def config_to_gain(self):
        return [g for g, c in self.GAINS.items() if c == self.config & self.GAIN_MASK][0]

    def config_to_lsb(self):
        return self.RESOLUTION_TO_LSB[self.config_to_resolution()]


    def __init__(self, address, resolution=18):
        self.address = address
        self.resolution = resolution

        self.scale_factor = 1.0
        self.offset = 0.09

        self.bus = smbus2.SMBus(1)

        self.config = 0
        self.configure()

    def configure(self):
        self.set_channel(0)
        self.set_gain(1)
        self.set_resolution(self.resolution)

        self.bus.write_byte(self.address, self.config)

    def set_channel(self, channel):
        self.config &= (~self.CHANNEL_MASK & 0x7f)
        self.config |= self.CHANNELS[channel]

    def set_gain(self, gain):
        self.config &= (~self.GAIN_MASK & 0x7f)
        self.config |= self.GAINS[gain]

    def set_resolution(self, resolution):
        self.config &= (~self.RESOLUTION_MASK & 0x7f)
        self.config |= self.RESOLUTIONS[resolution]

    def raw_read(self):
        self.config &= (~self.CONTINUOUS_MODE_MASK & 0x7f)
        self.config |= self.NOT_READY_MASK

        self.bus.write_byte(self.address, self.config)

        time.sleep(0.95 * self.RESOLUTION_TO_DELAY[self.resolution])

        bytes_to_read = 4 if self.resolution == 18 else 3

        while True:
            d = self.bus.read_i2c_block_data(self.address, self.config, bytes_to_read)
            config_used = d[-1]

            if config_used & self.NOT_READY_MASK == 0:
                count = 0
                for i in range(bytes_to_read - 1):
                    count <<= 8
                    count |= d[i]
                sign_bit_mask = 1 << (self.resolution - 1)
                count_mask = sign_bit_mask - 1
                sign_bit = count & sign_bit_mask
                count &= count_mask
                if sign_bit:
                    count = -(~count & count_mask) - 1
                return count, config_used

    def read(self, scale_factor=None, offset=None, raw=False):
        if scale_factor is None:
            scale_factor = self.scale_factor
        if offset is None:
            offset = self.offset

        count, config_used = self.raw_read()
        lsb = self.RESOLUTION_TO_LSB[self.resolution]

        voltage = (count * lsb * 1.0 / 1.0 / self.VD) + offset
        return voltage
