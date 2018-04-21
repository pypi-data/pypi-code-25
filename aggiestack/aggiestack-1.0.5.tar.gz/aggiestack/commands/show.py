"""The show command."""
  # aggiestack show hardware
  # aggiestack show images
  # aggiestack show flavors 
  # aggiestack show all 
  # aggiestack show logs 



from json import dumps

from .base import Base

from utils import image_utils
from utils import flavor_utils
from utils import hardware_utils
from utils import instance_utils
from utils import logger

class Show(Base):
    """Say hello, world!"""

    def run(self):
        #print('show, world!')
        #print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))
        if(self.options['images']):
            image_utils.getImageList()
        elif(self.options['flavors']):
            flavor_utils.getFlavorList()
        elif(self.options['hardware']):
            hardware_utils.getHardwareList()
        elif(self.options['logs']):
            logger.getLogs()
        elif(self.options['instances'] and self.options['show']):
            instance_utils.getInstanceList()
        elif(self.options['hardware'] and self.options['show']):
            hardware_utils.getInstanceList()
        elif(self.options['all']):
            print('\nImages : \n')
            image_utils.getImageList()
            print('\nFlavors : \n')
            flavor_utils.getFlavorList()
            print('\nHardware: \n')
            hardware_utils.getHardwareList()
            print('\nLogs: \n')
            logger.getLogs()
        else:
            logger.log("Invalid parameter",True)
