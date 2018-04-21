"""The config command."""

  # aggiestack config [--images=<IMAGES_PATH> | --flavors=<FLAVORS_PATH> | --hardware=<HARDWARE_PATH> ] -- done
  # aggiestack config load <CONGFIG_PATH>  

from json import dumps

from .base import Base

from utils import image_utils
from utils import flavor_utils
from utils import hardware_utils
from utils import logger
import os.path

class Config(Base):
    """Say hello, world!"""

    def run(self):
        print('config, world!')
        #print(self.options)
        if(self.options['--images']):
            image_list_path =  self.options['--images']
            image_utils.loadImageList(image_list_path)
        elif(self.options['--flavors']):
            flavor_list_path =  self.options['--flavors']
            flavor_utils.loadFlavorList(flavor_list_path)
        elif(self.options['--hardware']):
            hardware_list_path =  self.options['--hardware']
            hardware_utils.loadHardwareList(hardware_list_path)
        
