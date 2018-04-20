"""The server command."""

#   aggiestack server create [--image=<IMAGE> --flavor=<FLAVOR_NAME>] <INSTANCE_NAME>
#   aggiestack server delete <INSTANCE_NAME>
#   aggiestack server list

from json import dumps

from .base import Base

from utils import instance_utils
from utils import logger

class Server(Base):
    """Say hello, world!"""

    def run(self):
        #print('server, world!')
        #print(self.options)
        #print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))
        if(self.options['create']):
            print('create called')
            if(self.options['--image'] and self.options['--flavor']):
                
                instance = { 'instance_name' : self.options['<INSTANCE_NAME>'],
                             'flavor': self.options['--flavor'],
                             'image' :self.options['--image'] }
               
                instance_utils.createInstance(instance)
                
        elif (self.options['delete']):
            print('delete called')
            instance = {'instance_name' : self.options['<INSTANCE_NAME>']}
            instance_utils.deleteInstance(self.options['<INSTANCE_NAME>'])
            
            
        elif (self.options['list']):
            print('list called')
            instance_utils.getInstanceList()

