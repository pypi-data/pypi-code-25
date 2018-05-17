import logging


__all__ = [

     'getLogger'

]



def getLogger(name,filepath):

   # https://docs.python.org/2.3/lib/node304.html

   logger = logging.getLogger(name)


   handler = logging.FileHandler(filepath)

   formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

   handler.setFormatter(formatter)
   
   logger.addHandler(handler) 
   
   logger.setLevel(logging.DEBUG)


   return logger

