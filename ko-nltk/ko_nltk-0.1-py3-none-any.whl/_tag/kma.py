import konltk.c.kma
import os

class KltKma():
    def __init__(self, path = ""):
        self.dic_init()
        self.index_list = []
        self.input = ""
    
    def dic_init(self, path = ""):
        if path == "":
            if os.environ.get('KLT_DIC'):
                kdic_path = os.environ.get('KLT_DIC')
            else:
                kdic_path = ""
        else:
            kdic_path = path
        
        return konltk.c.kma.init(kdic_path)
        
    def set_data(self, data = ""):
        self.input == data
    
    
    def morpha(self, data = ""):
        self.set_data(data)
        self.morpha_list = konltk.c.kma.morpha(data)
        return self.morpha_list