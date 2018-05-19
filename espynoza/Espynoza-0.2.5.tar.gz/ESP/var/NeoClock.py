import machine

####################################################################################################

class NeoBuffer:
    C_RightMin =  10
    C_BottomMin = 20
    C_LeftMin   = 41
    C_TopMin    = 51
    
    C_TopBrightness    = 1.0
    C_RightBrightness  = 0.4
    C_BottomBrightness = 0.05
    C_LeftBrightness   = 0.6
    
    def __init__(self, p_Pixels):
        self.f_Pixels     = p_Pixels
        self.f_Buffer     = bytearray(self.f_Pixels * 3)
        self.f_Brightness = 1.0
        
    def clear(self):
        for l_i in range(len(self.f_Buffer)):
            self.f_Buffer[l_i] = 0
     
    def setPixel(self, p_Pixel, p_RGB):
        if   (p_Pixel < NeoBuffer.C_RightMin*3):
            l_SideBrightness = NeoBuffer.C_TopBrightness
        elif (p_Pixel < NeoBuffer.C_BottomMin*3):            
            l_SideBrightness = NeoBuffer.C_RightBrightness
        elif (p_Pixel < NeoBuffer.C_LeftMin*3):
            l_SideBrightness = NeoBuffer.C_BottomBrightness
        elif (p_Pixel < NeoBuffer.C_TopMin*3):
            l_SideBrightness = NeoBuffer.C_LeftBrightness
        else:
            l_SideBrightness = NeoBuffer.C_TopBrightness
        
        l_Offset         = (p_Pixel % self.f_Pixels) * 3
        self.f_Buffer[l_Offset:l_Offset+3] = bytes((int(p_RGB[1]*self.f_Brightness*l_SideBrightness), 
                                                    int(p_RGB[0]*self.f_Brightness*l_SideBrightness),
                                                    int(p_RGB[2]*self.f_Brightness*l_SideBrightness)
                                                  ))
                                              
####################################################################################################

def pixelString(p_PixelCount, p_Steps):    
    l_NeoBuffer  = NeoBuffer(p_PixelCount)
    l_Resolution = p_PixelCount // 60
    
    l_RTC = machine.RTC()
    l_RTC.datetime((2018,1,1,0,0,0,0,0))
           
    while True:
        l_NeoBuffer.clear()
        for l_Hours in range(12):
            if l_Hours % 3 == 0:
                l_NeoBuffer.setPixel(l_Hours * 5 * l_Resolution, (127,   0, 127))
            else:
                l_NeoBuffer.setPixel(l_Hours * 5 * l_Resolution, ( 31,   0,  31))

        l_Hours, l_Minutes, l_Seconds, l_Millis = l_RTC.datetime()[4:8]
        l_Hours   = l_Resolution * ((l_Hours + 2) * 5 + (l_Minutes * 5 // 60) )
        l_Minutes = l_Resolution * l_Minutes
        l_Seconds = l_Resolution * l_Seconds + l_Millis // 333

    # Hours
        l_NeoBuffer.setPixel((l_Hours-1)%p_PixelCount,  (   0,   0,  63))
        l_NeoBuffer.setPixel((l_Hours+0)%p_PixelCount,  (   0,   0, 255))
        l_NeoBuffer.setPixel((l_Hours+1)%p_PixelCount,  (   0,   0,  63))
        
    # Minutes
        l_NeoBuffer.setPixel(l_Minutes,                 (   0, 255,   0))
        
    # Seconds    
        if l_Seconds%3 == 0:
            l_NeoBuffer.setPixel((l_Seconds-1)%p_PixelCount, ( 63,  63,   0))
            l_NeoBuffer.setPixel((l_Seconds+0)%p_PixelCount, (255, 255,   0))
            l_NeoBuffer.setPixel((l_Seconds+1)%p_PixelCount, ( 31,  31,   0))
            
        elif l_Seconds%3 == 1:
            l_NeoBuffer.setPixel((l_Seconds-1)%p_PixelCount, (255, 255,   0))
            l_NeoBuffer.setPixel((l_Seconds+0)%p_PixelCount, ( 31,  31,   0))
            l_NeoBuffer.setPixel((l_Seconds+1)%p_PixelCount, ( 63,  63,   0))
        
        elif l_Seconds%3 == 2:
            l_NeoBuffer.setPixel((l_Seconds-1)%p_PixelCount, ( 31,  31,   0))
            l_NeoBuffer.setPixel((l_Seconds+0)%p_PixelCount, ( 63,  63,   0))
            l_NeoBuffer.setPixel((l_Seconds+1)%p_PixelCount, (255, 255,   0))
            
        yield l_NeoBuffer.f_Buffer   
        
