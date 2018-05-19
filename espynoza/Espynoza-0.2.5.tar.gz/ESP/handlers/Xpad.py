import machine

import BaseHandler

####################################################################################################
    
class Handler(BaseHandler.Handler):
    
    '''
        Target      : ESP8266,
        Description : Read the buttons on an XPad
        Parameters  : Period: The read frequency, in milliseconds 
                      Params:
                        - The Tag to use in MQTT topic
        Returns     : A byte, where each bit represents the value of the button (0 if pressed, else 1)   
    '''
    
    def __init__(self, p_Context):
        BaseHandler.Handler.__init__(self, p_Context)

        self.f_i2c     = machine.I2C(scl=self.f_Pins['SCL'], sda=self.f_Pins['SDA'])
        self.f_Buttons = 0xFF
        
######################### 

    def periodic(self, p_Now):
        try:
            l_NewButtons = self.f_i2c.readfrom(56, 1)[0]
            if l_NewButtons != self.f_Buttons:
                self.f_MQTT.publish('1/' + self.f_Params[0][0], l_NewButtons)
                self.f_Buttons = l_NewButtons
        except OSError as l_Exception:
                self.f_MQTT.publish('1/' + self.f_Params[0][0], str(l_Exception))
            
