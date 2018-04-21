"""The admin command."""


from json import dumps

from .base import Base

from utils import hardware_utils

from utils import logger


class AlterAdmin(Base):
    """Say hello, world!"""

    def run(self):
        #print('admin, world!')
        #print(self.options)
        #print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))

        if(self.options['add']):
                #(machineListPath,["hardware_name","rack_name","ip","RAM","numDisks","numVcpus"],'machine_collection')
                #print self.options
                machine = { 'hardware_name' : self.options['MACHINE'],
                            'rack_name' : self.options['RACK_NAME'],
                            'ip' : self.options['IP'],
                            'numVcpus' : self.options['VCPU'],
                             'RAM': self.options['MEM'],
                             'numDisks' :self.options['NUM_DISKS']
                              }
                hardware_utils.addHardware(machine)
                
        elif (self.options['remove']):
            print('remove called')
            hardware_utils.removeMachine(self.options['<MACHINE>'])

        elif (self.options['evacuate']):
            print('evacuate called')
            hardware_utils.evacuateRack(self.options['<RACK_NAME>'])
    
        elif (self.options['can_host']):
            print('can_host called')
            hardware_utils.isHardwareAvailable(self.options['<MACHINE_NAME>'],self.options['<FLAVOR>'])

        elif (self.options['clear_all']):
            testVar = raw_input('Are you sure you want to clear all y/n: ')
            if testVar == 'y': 
                hardware_utils.clear_all()

            