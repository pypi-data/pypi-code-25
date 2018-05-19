import time

import BaseHandler

####################################################################################################

class Handler (BaseHandler.Handler):
    '''
        Target      : ESP8266,
        Description : Set Digital output for a given duration
        Parameters  : Period: The check frequency, in milliseconds 
                      Params:
                        - The pin used for output
                        - The pulse width, in milliseconds
                        - Boolean, if True, then Pulse is active high
        Returns     : N/A   
    '''
    
    def __init__(self, p_Context):
        BaseHandler.Handler.__init__(self, p_Context)
        
        self.f_ToggleTime = {} # dictionary with pin name as key, value is ToggleTime: time when to toggle pin again, None if not triggered
        self.f_PulseWidth = {} # dictionary with pin name as key, value is Pulse width
        
        for l_Pin, l_PulseWidth, l_ActiveHigh in self.f_Params:
            self.f_ToggleTime[l_Pin] = None
            self.f_PulseWidth[l_Pin] = l_PulseWidth
            self.f_Pins[l_Pin].value(not(l_ActiveHigh))
            
#########################
        
    def periodic(self, p_Now):
        for l_Pin in self.f_ToggleTime.keys():
            if self.f_ToggleTime[l_Pin] is not None:
                if time.ticks_diff(p_Now, self.f_ToggleTime[l_Pin]) >= 0:
                    self.f_Pins[l_Pin].value(not(self.f_Pins[l_Pin].value()))
                    self.f_ToggleTime[l_Pin] = None

#########################

    def trigger(self, p_Pin, p_Width=0):
        self.f_Pins[p_Pin].value(not(self.f_Pins[p_Pin].value()))
        self.f_ToggleTime[p_Pin] = time.ticks_ms() + (self.f_PulseWidth[p_Pin] if (p_Width == 0) else p_Width)
        
        
        
        
