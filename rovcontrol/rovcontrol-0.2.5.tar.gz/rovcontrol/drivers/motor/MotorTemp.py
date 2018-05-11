import rovcontrol.drivers.DriverTemp as DriverTemp

class MotorTemp(DriverTemp.DriverTemp):
    default_channel_settings = {'speed' : 0, 'dir' : 0, 'sleep' : False, 'brake' : False, 'lock' : False, 'dirty' : True}
        
    def __init__(self, channels):
        self.settings = {}
        self.reglist = [
            {'name' : "speed", 'type' : int, 'depth' : 1,
             'set' : self.set_speed, 'get' : self.get_speed},
            {'name' : "dir", 'type' : int, 'depth' : 1,
             'set' : self.set_dir, 'get' : self.get_dir},
            {'name' : "sleep", 'type' : bool, 'depth' : 1,
             'set' : self.set_sleep, 'get' : self.get_sleep},
            {'name' : "brake", 'type' : bool, 'depth' : 1,
             'set' : self.set_brake, 'get' : self.get_brake},
            {'name' : "lock", 'type' : bool, 'depth' : 1,
             'set' : self.set_lock, 'get' : self.get_lock}]
        for i in channels:
            self.settings.update({i : dict(self.default_channel_settings)})
        self.update()
    def __str__(self):
        return str(self.settings)

    def update(self):
        for i in self.settings.keys():
            self.update_one_channel(i, self.settings[i])

    def update_one_channel(self, channel, data):
        data['dirty'] = False

    def set_speed(self, channel, speed):
        channel = int(channel)
        self.settings[channel]['speed'] = speed
        self.settings[channel]['dirty'] = True
        self.update()
    def get_speed(self, channel):
        channel = int(channel)
        return self.settings[channel]['speed']

    def set_dir(self, channel, direction):
        channel = int(channel)
        self.settings[channel]['dir'] = direction
        self.settings[channel]['dirty'] = True
        self.update()
    def get_dir(self, channel):
        channel = int(channel)
        return self.settings[channel]['dir']

    def set_brake(self, channel, brake):
        channel = int(channel)
        self.settings[channel]['brake'] = brake
        self.settings[channel]['dirty'] = True
        self.update()
    def get_brake(self, channel):
        channel = int(channel)
        return self.settings[channel]['brake']

    def set_lock(self, channel, lock):
        channel = int(channel)
        self.settings[channel]['lock'] = lock
        self.settings[channel]['dirty'] = True
        self.update()
    def get_lock(self, channel):
        channel = int(channel)
        return self.settings[channel]['lock']

    def set_sleep(self, channel, sleep):
        channel = int(channel)
        self.settings[channel]['sleep'] = sleep
        self.settings[channel]['dirty'] = True
        self.update()
    def get_sleep(self, channel):
        channel = int(channel)
        return self.settings[channel]['sleep']

    def set_speed_fancy(self, channel, fancyspeed):
        channel = int(channel)
        self.set_dir(channel, 0 if speed >= 0 else 1)
        self.set_speed(channel, abs(fancyspeed))
