import konltk.c.index
import os

class KltIndex:


    def __init__(self, path = ""):
        self.dic_init(path)
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
        
        return konltk.c.index.init(kdic_path)
    
    def set_data(self, data = ""):
        self.input == data

    def index(self, data = ""):
        self.set_data(data)
        self.index_list = konltk.c.index.index(data)

        return self.index_list

    def noun_comp(self, data = "", separator = " "):
        return konltk.c.index.noun_comp(data, separator[0])