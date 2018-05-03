import yaml
from DeploymentFunctions import ImcInstance
import time
import sys

#You need to specify the config file when running the script
with open(sys.argv[1], 'r') as stream:
    try:
        fullConfig = yaml.load(stream)
        ImcInstanceObj = ImcInstance(fullConfig['initialIMCHandleConnection']['ipAddress'],
                                  fullConfig['initialIMCHandleConnection']['username'],
                                  fullConfig['initialIMCHandleConnection']['password'])
        ImcInstanceObj.setNewPasword(fullConfig['setNewPassword']['password'])
        ImcInstanceObj.mgmtInterfaceConfigInOneGo(fullConfig['mgmtInterfaceConfigInOneGo']['newIPAddress'],
                                               fullConfig['mgmtInterfaceConfigInOneGo']['newMask'],
                                               fullConfig['mgmtInterfaceConfigInOneGo']['newDG'],
                                               fullConfig['mgmtInterfaceConfigInOneGo']['newHostname'],
                                               fullConfig['mgmtInterfaceConfigInOneGo']['newDNS'],)
        print 'pausing for 60 seconds...'
        for x in range(1, 61):
            print x
            time.sleep(1)
        print '...continuing...'

        ImcInstanceObj = ImcInstance(fullConfig['secondIMCHandleConnection']['ipAddress'],
                                  fullConfig['secondIMCHandleConnection']['username'],
                                  fullConfig['secondIMCHandleConnection']['password'])

        ImcInstanceObj.setNTP(fullConfig['setNTP']['ipAddress'])

        ImcInstanceObj.setSNMP(fullConfig['setSNMP']['port'],
                             fullConfig['setSNMP']['community'],
                             fullConfig['setSNMP']['systemContact'],
                             fullConfig['setSNMP']['location'],
                             fullConfig['setSNMP']['trapCommunity'],
                             fullConfig['setSNMP']['trapIPAddress'],
                             fullConfig['setSNMP']['id'])

        for syslogServer in fullConfig['setSyslog']:
            ImcInstanceObj.setSyslog(syslogServer['ipAddress'],syslogServer['role'])

        ImcInstanceObj.setPowerPolicy()
        ImcInstanceObj.setFanPolicy()
        ImcInstanceObj.powerOnServer()

        print 'pausing for 1 min...'
        for x in range(1, 61):
            print x
            time.sleep(1)

        print '...continuing...'
        ImcInstanceObj.setRAID1()
        ImcInstanceObj.setBootDriveAndInitialize()
        ImcInstanceObj.setBootOrder()
        ImcInstanceObj.logout()

    except yaml.YAMLError as exc:
        print exc

