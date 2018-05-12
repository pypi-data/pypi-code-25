class ComTemp:
    def __init__(self):
        self.settings = {}
    def __str__(self):
        return str(self.settings)

    def add_driver(self, driver, name):
        self.settings.update({name : driver})

    def getr(self, drivername, regname, *args):
        return self.settings[drivername].get_reg(regname, *args)
    def setr(self, drivername, regname, value, *args):
        return self.settings[drivername].set_reg(regname, value, *args)
