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

        if 'lease ' in lineInDHCPSrvFile:
            ip = lineInDHCPSrvFile.split(' ')[1]

        if 'uid' in lineInDHCPSrvFile:
            uid = lineInDHCPSrvFile.split('"')[1]
            uidCounter = lineCounter

        # Checks to see if the DHCP entry at the ISC-DHCP dhcpd.lease file is indeed an IMC server, and checks
        # that the UID filed is right above it. There have been issues with PXE Clients without UIDs. Why?
        # This sould definetly be checked.
        if 'PXEClient:Arch:00000:UNDI:002001' in lineInDHCPSrvFile and lineCounter == uidCounter+1:
            if uid not in open('/etc/imcautodeploy/alreadyProvisioned.txt').read():
                # Check to see if a config file exist for this new IMC server
				configFileLocation = '/etc/imcautodeploy/config/'
				listOfCreatedIMCConfigFiles = [f for f in listdir(configFileLocation) if isfile(join(configFileLocation,f))]
				theFirstThreeOctetsOfNewIP = str(ip.split('.'))[0]+'.'+ip.split('.'))[1]+'.'+ip.split('.'))[2]+'.yaml'
				if theFirstThreeOctetsOfNewIP in listOfCreatedIMCConfigFiles:
					#finally initialize the IMC
					print('A new server with IP address '+ip+' has been detected and is now being provisioned')
					configureIMC('/etc/imcautodeploy/config/'+theFirstThreeOctetsOfNewIP)
                with open('/etc/imcautodeploy/alreadyProvisioned.txt','a') as fileToAddNewlyProvisionedIMCsTo:
                    fileToAddNewlyProvisionedIMCsTo.write(uid+' which originally got this IP address: '+ip+'\n')

