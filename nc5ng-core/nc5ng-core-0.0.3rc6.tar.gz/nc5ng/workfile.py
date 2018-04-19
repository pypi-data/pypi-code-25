


class Control(object):
    
    def __init__(self, control_filename):
        self.f = open(control_filename, 'r')
        __init_parse__()


    def __init_parse__(self):
        
