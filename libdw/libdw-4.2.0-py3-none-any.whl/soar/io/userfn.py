class UserFunctionIF():
    def __init__(self):
        self.fn = {'setup': [],
                   'brain_start': [],
                   'step': [],
                   'brain_stop': [],
                   'shutdown': []}

    def registerFn(self, type, f):
        self.fn[type].append(f)

    def call_functions(self, type):
        for f in self.fn[type]:
            f()

    def clearFunctions(self):
        for k in list(self.fn.keys()):
            self.fn[k] = []
            

    
