import konltk.c.codescan as D


class Detect:


    def checkFileText(self):
        try:
            self.file = open(self.text, "rb")
            self.type = "FILE"
        except:
            self.type = "TEXT"

    def __init__(self, text = ""):
        self.setText(text)

    def setMax(self, max = 30):
        if max <= 0:
            max = len(self.len)
        
        self.max = max

    def setText(self, text = ""):
        self.text = text
        self.checkFileText()

        if self.type == "FILE":
            self.text = self.file.read()
            # file to text by line

    def detect(self, text = "", max = 30):
        if len(self.text) is 0:
            if text == "":
                return "Don't have any text"
            else:
                self.setText(text)

        if self.type is "TEXT" and type(self.text) is str:
            return "you have to using byte array"
        self.setMax(max)

        d = D.detect(self.text, len(self.text), self.max)
        
        if d is 0:
            return "NONE"
        elif d is 1:
            return "EUCKR"
        elif d is 2:
            return "UTF8"
        elif d is 3:
            return "UTF16BE"
        else:
            return "UTB16LE"

