import os
import konltk.c.asp as asp


class KltAsp:


    def __init__(self, path = ""):
        self.dic_init()
        self.input = ""

    def dic_init(self, path = ""):
        kdic_path = ""

        if path == "":
            if not (os.environ.get("KLT_AUTOSPACE_DIC") is None):#os.environ["KLT_AUTOSPACE_DIC"]
                kdic_path = os.environ.get("KLT_AUTOSPACE_DIC")
        else:
            kdic_path = path
        
        return asp.init(kdic_path)
    
    def set_data(self, data = ""):
        self.input = data

    def asp(self, data = ""):
        self.set_data(data)

        return asp.asp(self.input)