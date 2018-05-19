import BaseHandler

####################################################################################################

class Handler (BaseHandler.Handler):
    '''
        Target      : ESP8266,
        Description : Set Digital output
        Parameters  : Period: the period if blinking is true, in milliseconds
                      Params:
                        - The pin used for output
                        - Boolean, if True, blink output
        Returns     : N/A   
    '''
    
    def __init__(self, p_Context):
        BaseHandler.Handler.__init__(self, p_Context)

        self.f_States = { l_Pin : False for l_Pin, l_Blink in self.f_Params}

#########################
        
    def periodic(self, p_Now):
        for l_Pin, l_Blink in self.f_Params:
            if l_Blink:
                self.toggle(l_Pin)

#########################

    def set(self, p_Pin, p_State):
        self.f_States[p_Pin] = int(p_State)
        self.f_Pins  [p_Pin].value(int(p_State))
        
#########################

    def toggle(self, p_Pin):
        self.f_States[p_Pin] = not self.f_States[p_Pin]
        self.f_Pins  [p_Pin].value(self.f_States[p_Pin])
        
