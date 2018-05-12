import rovcontrol.drivers.com.ComTemp as ComTemp

class DummyCom(ComTemp.ComTemp):
    def listen(self):
        while True:
            op, *arg, x= input("--> ").split(" ")
            if op == "get":
                print(self.getr(arg[0], arg[1], *(arg[2:len(arg)])))
            if op == "set":
                self.setr(arg[0], arg[1], x, *(arg[2:len(arg)]))
