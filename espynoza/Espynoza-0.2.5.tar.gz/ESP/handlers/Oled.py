import framebuf
import machine
import time

from micropython import const

import BaseHandler

####################################################################################################

class Handler (BaseHandler.Handler):
    '''
        Target      : ESP8266,
        Description : Set OLED  using I2C
        Parameters  : Period: Refresh period
                      Params:
                        None
        Returns     : N/A   
    '''

        
    def __init__(self, p_Context):
        BaseHandler.Handler.__init__(self, p_Context)
        
        self.C_ProbeCount = 5

        l_I2C  = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))   
        self.f_Oled = SSD1306_I2C(l_I2C)

        self.f_XState     = 0
        self.f_Individual = False
        
        self.reset()
        

######################### 

    def reset(self):
        self.f_Min   = [1024 for l_i in range(self.C_ProbeCount)]
        self.f_Max   = [   0 for l_i in range(self.C_ProbeCount)]
        self.f_Total = [   0 for l_i in range(self.C_ProbeCount)]
        
        self.f_Count = 0
        
######################### 

    def periodic(self, p_Now):
        C_Colors = ['C', 'R', 'S', 'G', 'B']
        
        l_Buttons = self.f_User["Xpad"]["Handler"].f_Buttons
        if l_Buttons != 0xFF:
            if   l_Buttons == 247:
                self.reset()
            elif l_Buttons == 251:
                self.f_XState = (self.f_XState - 1) % 4 # this is 4, unrelated to # of probes!
            elif l_Buttons == 253:
                self.f_XState = (self.f_XState + 1) % 4
            elif l_Buttons == 254:
                self.f_Individual = not self.f_Individual
                
            self.f_Oled.invert(1)
            time.sleep(0.5)
            self.f_Oled.invert(0)
                
        l_Temperatures = self.f_User["DS18B20"]["Handler"].f_Temperatures
        
        for l_i, l_Temp in enumerate(l_Temperatures):
            if l_Temp is None:
                return
            
            self.f_Min  [l_i]  = min (self.f_Min[l_i], l_Temp)
            self.f_Max  [l_i]  = max (self.f_Max[l_i], l_Temp)
            self.f_Total[l_i] += l_Temp
            
        self.f_Count += 1
            
        self.f_Oled.fill(0) 
        
        if self.f_Individual:
            self.f_Oled.text(C_Colors[self.f_XState], 28, 0)
            self.f_Oled.text("Ak{:6.2f}".format(l_Temperatures[self.f_XState]              ), 0,  9)
            self.f_Oled.text("Mi{:6.2f}".format(self.f_Min    [self.f_XState]              ), 0, 18)
            self.f_Oled.text("Ma{:6.2f}".format(self.f_Max    [self.f_XState]              ), 0, 27)
            self.f_Oled.text("Mo{:6.2f}".format(self.f_Total  [self.f_XState]/self.f_Count ), 0, 36)
                
        else:
            if self.f_XState == 0:
                self.f_Oled.text("Aktuell", 4, 0)
                l_Values = l_Temperatures
                    
            elif self.f_XState == 1:
                self.f_Oled.text("Min", 20, 0)
                l_Values = self.f_Min
                    
            elif self.f_XState == 2:
                self.f_Oled.text("Max", 20, 0)
                l_Values = self.f_Max
                    
            elif self.f_XState == 3:
                self.f_Oled.text("Moyenne", 4, 0)
                l_Values = [l_Total/self.f_Count for l_Total in self.f_Total]
            
            for l_i, l_Temp in enumerate(l_Values):
                if l_i > 3:
                    break
                self.f_Oled.text("{:1s} {:6.2f}".format(C_Colors[l_i],l_Temp), 0, (l_i+1)*9)
                
        self.f_Oled.show()
        
####################################################################################################
####################################################################################################

# MicroPython SSD1306 OLED driver, I2C interface only


# register definitions
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xa4)
SET_NORM_INV        = const(0xa6)
SET_DISP            = const(0xae)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xa0)
SET_MUX_RATIO       = const(0xa8)
SET_COM_OUT_DIR     = const(0xc0)
SET_DISP_OFFSET     = const(0xd3)
SET_COM_PIN_CFG     = const(0xda)
SET_DISP_CLK_DIV    = const(0xd5)
SET_PRECHARGE       = const(0xd9)
SET_VCOM_DESEL      = const(0xdb)
SET_CHARGE_PUMP     = const(0x8d)


class SSD1306:
    def __init__(self):
        self.pages    = 6
        self.buffer   = bytearray(self.pages * 64)
        self.framebuf = framebuf.FrameBuffer(self.buffer, 64, 48, framebuf.MVLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
                    SET_DISP | 0x00, # off
                    # address setting
                    SET_MEM_ADDR, 0x00, # horizontal
                    # resolution and layout
                    SET_DISP_START_LINE | 0x00,
                    SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
                    SET_MUX_RATIO, 48 - 1,
                    SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
                    SET_DISP_OFFSET, 0x00,
                    SET_COM_PIN_CFG,  0x12,
                    # timing and driving scheme
                    SET_DISP_CLK_DIV, 0x80,
                    SET_PRECHARGE,  0xf1,
                    SET_VCOM_DESEL, 0x30, # 0.83*Vcc
                    # display
                    SET_CONTRAST, 0xff, # maximum
                    SET_ENTIRE_ON, # output follows RAM contents
                    SET_NORM_INV, # not inverted
                    # charge pump
                    SET_CHARGE_PUMP, 0x14,
                    SET_DISP | 0x01
                   ): # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 32
        x1 = 95
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)

    def fill(self, col):
        self.framebuf.fill(col)
        return self

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)
        return self

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)
        return self

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)
        return self

    def para(self, p_Lines):
        self.fill(0)
        for l_i, l_Line in enumerate(p_Lines):
            self.text(l_Line, 0, l_i*8)
        return self
            
class SSD1306_I2C(SSD1306):
    def __init__(self, i2c, addr=0x3c):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        super().__init__()

    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.temp[0] = self.addr << 1
        self.temp[1] = 0x40 # Co=0, D/C#=1
        self.i2c.start()
        self.i2c.write(self.temp)
        self.i2c.write(buf)
        self.i2c.stop()
