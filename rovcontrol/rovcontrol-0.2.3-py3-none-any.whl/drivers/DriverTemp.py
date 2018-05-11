class DriverTemp:
    def __init__(self):
        self.settings = {}

    def get_reg_list(self):
        return self.reglist

    def get_reg_type(self, regname):
        for i in self.get_reg_list():
            if i['name'] == regname:
                return i['type']

    def get_reg(self, regname, *args):
        for i in self.get_reg_list():
            if i['name'] == regname:
                return i['get'](*args)
    def set_reg(self, regname, value, *args):
        for i in self.get_reg_list():
            if i['name'] == regname:
                return i['set'](*args, self.get_reg_type(regname)(value))
