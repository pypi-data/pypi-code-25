import connect_db
import os.path
import logger

import database
import flavor_utils

def loadHardwareList(hardwareListPath):
    rackListPath, machineListPath = splitFile(hardwareListPath)
    database.loadList(rackListPath,["rack_name","space"],'rack_collection')
    database.loadList(machineListPath,["hardware_name","rack_name","ip","RAM","numDisks","numVcpus"],'machine_collection')

def getHardwareList():
    print ("These are the machines configured on the server")
    database.getList('machine_collection')
    print ("These are the racks configured on the server")
    database.getList('rack_collection')

def clearHardwareList():
    database.clearList('rack_collection')
    database.clearList('machine_collection')

def clear_all():                                  #To be moved to database
    database.clearList('rack_collection')
    database.clearList('machine_collection')
    database.clearList('log_collection1')
    database.clearList('flavor_collection')
    database.clearList('image_collection')
    database.clearList('instance_collection')

def addMachine(item_dict):
    database.addItem(item_dict,'machine_collection')    

def removeMachine(machine_name, avoid_rack = None):
    machine = database.getItem('hardware_name',machine_name,'machine_collection')
    instances = machine['instances']
    database.deleteItem('hardware_name',machine_name,'machine_collection')
    for instance in instances:
        allocateHardware(instance,avoid_rack = None)

def evacuateRack(rack_name):
    print('evacuating rack...')
    machines = database.getList('machine_collection', display=False)
    for machine in machines:
        if machine['rack_name'] == rack_name :
            removeMachine(machine['hardware_name'], avoid_rack=rack_name)

def isHardwareAvailable(machine_name, flavor_name):
    can_host = False
    machine = database.getItem('hardware_name',machine_name,'machine_collection')
    flavor  = flavor_utils.getFlavor('flavor_name')
    if(int(machine['RAM'])>=int(flavor['RAM']) and
       int(machine['numDisks'])>=int(flavor['numDisks']) and
       int(machine['numVcpus'])>=int(flavor['numVcpus']) ):
        logger.log('Can host instance')
        can_host = True
        return True
    if not can_host:
        logger.log('Cannot host instance')
    return False


def addHardware(addToMachine):
    added = False
    machine = database.getItem('hardware_name',addToMachine['hardware_name'],'machine_collection')
    if machine['ip'] == addToMachine['ip']:              
        machine['RAM']     =str(int(machine['RAM']     ) +int(addToMachine['RAM'])     )
        machine['numDisks']=str(int(machine['numDisks']) +int(addToMachine['numDisks']))
        machine['numVcpus']=str(int(machine['numVcpus']) +int(addToMachine['numVcpus']))
        database.updateItem(machine,'machine_collection')
        print('Succesfully updated machine specifications')
        logger.log('Succesfully updated machine specs')
        added = True
        return True
    if not added:
        logger.log('HARDWARE ERROR : Failed to add additional memory',True)
    return False    

def allocateHardware(instance,avoid_rack = None):
    added = False
    machineList = database.getList('machine_collection',display=False)

    for machine in machineList:
        #print machine

        if(int(machine['RAM'])>=int(instance['RAM']) and
           int(machine['numDisks'])>=int(instance['numDisks']) and
           int(machine['numVcpus'])>=int(instance['numVcpus']) and
           machine['rack_name'] != avoid_rack ):
            
            machine['RAM']     =str(int(machine['RAM']     ) -int(instance['RAM'])     )
            machine['numDisks']=str(int(machine['numDisks']) -int(instance['numDisks']))
            machine['numVcpus']=str(int(machine['numVcpus']) -int(instance['numVcpus']))
            machine.setdefault('instances',[]).append(instance)
            print "Server found, Calling update"
            database.updateItem(machine,'machine_collection')
            item = database.getItem('ip',machine['ip'],'machine_collection')
            print instance['instance_name'] , 'added to server on ip ', item['ip'],' in rack ',machine['rack_name'] 
            logger.log('added instance to the system')
            added = True
            return True
    if not added:
        logger.log('Faild to add',True)
    return False

def deallocateHardware(instance):
    removed = False
    
    machineList = database.getList('machine_collection',display=False)
    #print (machineList)
    for machine in machineList:
        #print (machine)
        if 'instances' in machine:  
            for existing_instance in machine['instances']:
                if instance['instance_name'] == existing_instance['instance_name']:              
                    machine['RAM']     =str(int(machine['RAM']     ) +int(instance['RAM'])     )
                    machine['numDisks']=str(int(machine['numDisks']) +int(instance['numDisks']))
                    machine['numVcpus']=str(int(machine['numVcpus']) +int(instance['numVcpus']))
                    machine['instances'].remove(existing_instance)
                    database.updateItem(machine,'machine_collection')
                    logger.log('removed instance from the system')
                    removed = True
                    return True
    if not removed:
        logger.log('HARDWARE ERROR : Failed to remove',True)
    return False

def splitFile(hardwareListPath):
    if(os.path.isfile(hardwareListPath)):
        with open(hardwareListPath, "r") as fp:
            lines  = fp.readlines()
            lines = [x.strip() for x in lines] 
            #print lines
            racks = lines[0:int(lines[0])+1]
            machines = lines[int(int(lines[0])+1):]
            rackListPath = './racks.txt'
            machineListPath = './machines.txt'
            with open(rackListPath, "w") as rackfile:
                for rack in racks:
                    rackfile.write("%s\n" % rack)
            with open(machineListPath, "w") as machinefile:
                for machine in machines:
                    machinefile.write("%s\n" % machine)
            return rackListPath, machineListPath
            


    