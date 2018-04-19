"""
colorThis by Denver P.

Adapted implementation of Colorama
"""

import os # used to allow win32 console to recognize ANSI/VT100 escape sequences

coloramaImported = False
try: # attempt to import colorama
    import colorama # library used for colouring
    coloramaImported = True # set variables if no errors raised
except: # if importing colourama raised an error
    pass # do nothing (coloramaImported remains False)
    
''' variables '''
reset_char = '\x1b[0m' # ANSI character to reset all styling

''' fixes '''
os.system('') # stops formatting from appearing as "[41m[33m" and the like

''' define functions '''
def ct(my_string,**kwargs): # define main function
    ''' EXAMPLE: ct("hello",Back="RED") '''
    
    func_kws = {'debug': False,'autoReset': True,'showErrors': True} # List of keywords that change how this function executes
    styleKWs = ['Back','Fore','Style'] # list of classes from colorama that are compatible with this function
    
    for func_kw in func_kws: # for each keyword we can process
        if(func_kw in kwargs): # check if it's in the kwargs parsed, and if it is
            func_kws[func_kw] = kwargs[func_kw] # change the local keyword value to the parsed keyword value
            
    out = []
    
    if (coloramaImported): # if colorama imported successfully
        for kwarg in kwargs: # for each kwarg parsed
            if kwarg in styleKWs: # if this kwarg is a styling keyword
                out.append(eval('colorama.%s.%s' % (kwarg,kwargs[kwarg]))) # append the colorama class to the list
                
            elif kwarg in func_kws: # if this kwarg is a function keyword
                pass # do nothing
                
            else: # if this kwarg is not a recognized keyword
                if(func_kws['showErrors']): # if raising/displaying errors is on (True)
                    raise Exception('{} is not a compatible keyword'.format(kwarg)) # raise an error stating the keyword is incompatible
                    
        if not (my_string == ""): # if my_string IS NOT empty
            out.append(str(my_string)) # append the inputed string to the output list
            
        if(func_kws['autoReset']): # if autoReset is enabled
            out.append(colorama.Style.RESET_ALL) # append a style reset character to the end of the list
            
        out = "".join(out) # convert the output array into a string
        
        return(out)
    
    else: # if colorama didn't import successfully
        if(func_kws['showErrors']): # if raising/displaying errors is on (True)
            print("colorama could not be imported... maybe it isn't installed? Maybe you're running 64-bit instead of 32-bit?")
            print("returning a normal string...")
        return(my_string)
        
        
        
def ct_hex(my_string,hex_color,**kwargs):
    ''' change terminal text colour to a hexadecimal value'''
    
    autoReset=True
    if 'autoReset' in kwargs: autoReset = kwargs['autoReset'] # store value of autoReset if found in kwargs
    
    r, g, b = [int(hex_color[i:i+2], 16) for i in range(1, len(hex_color), 2)] # convert hexadecimal value to R,G,B components, store resulting values
    out = "\x1b[38;2;{};{};{}m{}".format(r,g,b,my_string)
    if(autoReset): out = out + reset_char
    return(out)
    #hex_color = '#f57c00'
    # thanks to Ican for his answer on stackoverflow: https://stackoverflow.com/a/41063750/5619653

def ct_rgb(my_string,r,g,b,**kwargs):
    ''' change terminal text colour to an RGB value'''
    
    autoReset=True
    if 'autoReset' in kwargs: autoReset = kwargs['autoReset'] # store value of autoReset if found in kwargs
    
    out = "\x1b[38;2;{};{};{}m{}".format(r,g,b,my_string)
    if(autoReset): out = out + reset_char
    
    return(out)
    
def runTest():
    print(ct("defined colour",Fore="RED"))
    print("normal text")
    print(ct_hex("hex colour!",'#f57c00'))
    print("normal text")
    print(ct_rgb("rgb colors",255,0,0))
    print("normal text")
    
    import time
    def ct_grad(char='.',duration=1,instances=16,time_div_dec_places=8):
        x = 1
        while(x < 255):
            time.sleep(round(duration/instances,time_div_dec_places))
            print(ct_rgb(char,0,x,0),end='',flush=True)
            x += int(255/instances)
        return('')
            
    print(ct_grad('.',1,16))
    print("HEHELLO")
    print("HEHELLO")
    
