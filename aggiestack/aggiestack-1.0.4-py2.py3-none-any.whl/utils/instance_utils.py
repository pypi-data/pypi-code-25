import connect_db
import logger
import image_utils
import flavor_utils
import hardware_utils
import database


# def loadInstanceList(instanceListPath):
#     database.loadList(instanceListPath,["instance_name","flavor","image"],'instance_collection')

def getInstanceList():
    print ("These are the instances configured on the server")
    #database.getList('instance_collection')  
    machineList = database.getList('machine_collection',display=False)
    for machine in machineList:
        if 'instances' in machine:
            for instance in machine['instances']:
                print machine['ip'], " | " ,machine['rack_name'] , " | ", instance['instance_name']

    
def getInstance(instance_name, no_error = False):
    return database.getItem('instance_name',instance_name,'instance_collection',no_error)


def clearInstanceList():
    database.clearList('instance_collection')

def isValidInstance(instance):
    return image_utils.isValidImage(instance['image']) and flavor_utils.isValidFlavor(instance['flavor']) 
      

def createInstance(instance):
    if(isValidInstance(instance) and getInstance(instance['instance_name'],no_error=True) == None):
        flavor = flavor_utils.getFlavor(instance['flavor'])
        instance['RAM']=flavor['RAM']
        instance['numDisks']=flavor['numDisks']
        instance['numVcpus']=flavor['numVcpus']

        if(hardware_utils.allocateHardware(instance)):
            database.addItem(instance,'instance_collection')
            logger.log('Successfully added new instance to the cluster')
    else:
        logger.log('Failed to add new instance to the cluster.An instance of same name already exists',True)        
        
def deleteInstance(instance_name):
    #print (getInstance(instance_name))
    if (getInstance(instance_name) != None):
        instance  = getInstance(instance_name)
        hardware_utils.deallocateHardware(instance)
        database.deleteItem('instance_name',instance_name,'instance_collection')
        logger.log('Successfully removed instance from the cluster')
    else:
        logger.log('Failed to remove instance from the cluster',True)

