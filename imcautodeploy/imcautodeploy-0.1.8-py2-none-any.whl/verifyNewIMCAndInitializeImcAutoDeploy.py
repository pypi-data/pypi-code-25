# Initialize IMC automation script
# Author Alexander Aasen
# This script will check if a new server has received a DHCP lease, then start the automation script

from imcautodeploy.autodeployBasedOnYAMLConfigFile import configureIMC
from os import listdir
from os.path import isfile, join

with open('/var/lib/dhcpd/dhcpd.leases') as dhcpSrvFil:
    lineCounter = 0
    uidCounter = 0
    ip = 'rdmPlaceholderString'
    uid = 'rdmPlaceholderString'

    for lineInDHCPSrvFile in dhcpSrvFil:
        lineCounter = lineCounter+1

        # Finds the IP address of the server
        if 'lease ' in lineInDHCPSrvFile:
            ip = lineInDHCPSrvFile.split(' ')[1]

        # Finds the UID of the server
        if 'uid' in lineInDHCPSrvFile:
            uid = lineInDHCPSrvFile.split('"')[1]
            uidCounter = lineCounter

        # Checks if the DHCP lease is for a IMC device, and that UID is listed directly above
        if 'PXEClient:Arch:00000:UNDI:002001' not in lineInDHCPSrvFile or lineCounter != uidCounter+1:
            continue
        
        # Checks if the IMC server has already been provisioned
        if uid in open('/etc/imcautodeploy/alreadyProvisioned.txt').read():
            continue

        # Should be syslog
        print 'The IMC server with ip: '+ip+' has not yet been provisioned'

        # Checks that the server config file exists
        configFileLocation = '/etc/imcautodeploy/config/'
        listOfCreatedIMCConfigFiles = [f for f in listdir(configFileLocation)
            if isfile(join(configFileLocation,f))]
        theFirstThreeOctetsOfNewIP = str(ip.split('.')[0])+'.'+str(ip.split('.')[1])+'.'\
                                             +str(ip.split('.')[2])+'.yaml'
        if theFirstThreeOctetsOfNewIP not in listOfCreatedIMCConfigFiles:
            # This should be syslog
            print 'The IMC server does not yet have a config file'
            continue
        
        # Checks if the IP address is what it should already be. The IP should not have been .12
        if ip.split('.')[3] == str(12):
            # should be syslog
            print 'The IMC server got the wrong IP address of '+str(ip)
            continue

        # If all tests passed, then initialize the server. This should also be syslog
        print 'A new server with IP address '+ip+\
                      ' has been detected and is now being provisioned'
        configureIMC('/etc/imcautodeploy/config/'+theFirstThreeOctetsOfNewIP)
        
        # Updates the list over already provisioned IMC servers
        with open('/etc/imcautodeploy/alreadyProvisioned.txt','a') as fileToAddNewlyProvisionedIMCsTo:
            fileToAddNewlyProvisionedIMCsTo.write(uid+' which originally got this IP'+
                    'address: '+ip+'\n')

