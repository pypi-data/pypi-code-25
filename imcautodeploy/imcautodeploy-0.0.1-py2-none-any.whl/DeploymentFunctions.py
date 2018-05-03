from imcsdk.imchandle import ImcHandle
from imcsdk.mometa.comm.CommSnmpTrap import CommSnmpTrap
from imcsdk.mometa.comm.CommSyslogClient import CommSyslogClient
from imcsdk.mometa.storage.StorageVirtualDriveCreatorUsingUnusedPhysicalDrive import \
    StorageVirtualDriveCreatorUsingUnusedPhysicalDrive
from imcsdk.apis.server.serveractions import server_power_up
from imcsdk.apis.server.boot import boot_order_precision_set
import re


class ImcInstance:
    def __init__(self, IPAddress, username, password):
        self.handle = ImcHandle(IPAddress, username, password)
        try:
            if self.handle.login():
                print '- login successful'
        except Exception as e:
            print '- login failed with the error message: ' + str(e)
            print '- trying to login again'
            if self.handle.login():
                print '- login successful'

    def setNewPasword(self, passord):
        try:
            adminBruker = self.handle.query_classid('aaaUser')[0]
            adminBruker.pwd = passord
            self.handle.set_mo(adminBruker)
            print '- password updated'
        except Exception as e:
            print '- something went wrong with setting a new password: ' + str(e)
            return

    def mgmtInterfaceConfigInOneGo(self,IpAddress=None, mask=None, defaultGateway=None, hostname=None,
                            dns_preferred=None, dns_alternate=None):
        try:
            mgmtInterface = self.handle.query_classid('MgmtIf')[0]
            mgmtInterface.dns_using_dhcp = 'no'
            mgmtInterface.dhcp_enable = 'no'
            mgmtInterface.ext_ip = IpAddress
            mgmtInterface.ext_mask = mask
            mgmtInterface.ext_gw = defaultGateway

            mgmtInterface.dns_preferred = dns_preferred
            mgmtInterface.dns_alternate = dns_alternate

            mgmtInterface.hostname = hostname

            mgmtInterface.nic_mode = 'dedicated'
            mgmtInterface.nic_redundancy = 'none'
            mgmtInterface.auto_neg = 'Enabled'

            self.handle.set_mo(mgmtInterface)
            print '- DHCP turned off'
            print '- new IP address: ' + str(mgmtInterface.ext_ip) + ' mask: ' + str(mgmtInterface.ext_mask)
            print '- default gateway: ' + str(mgmtInterface.ext_gw)

            print '- preferred DNS server configured with IP address: ' + str(dns_preferred)
            print '- alternate DNS server configured with IP address: ' + str(dns_alternate)

            print '- hostname configured as: ' + hostname

            print '- NIC configured as dedicated, redundancy to none and duplex and speed to auto'

        except Exception as e:
            print '- something went wrong when configuring the management interface:  ' + str(e)
            return

    def setIpAddress(self, IpAddress, mask, defaultGateway):
        try:
            mgmtInterface = self.handle.query_classid('MgmtIf')[0]
            mgmtInterface.dns_using_dhcp = 'no'
            mgmtInterface.dhcp_enable = 'no'
            mgmtInterface.ext_ip = IpAddress
            mgmtInterface.ext_mask = mask
            mgmtInterface.ext_gw = defaultGateway
            self.handle.set_mo(mgmtInterface)
            print '- DHCP turned off'
            print '- new IP address: ' + mgmtInterface.ext_ip + ' mask: ' + mgmtInterface.ext_mask
            print '- default gateway: ' + mgmtInterface.ext_gw
        except Exception as e:
            print '- something went wrong with setting a new IP address: ' + str(e)
            return

    def setDNS(self, dns_preferred=None, dns_alternate=None):
        try:
            mgmtInterface = self.handle.query_classid('MgmtIf')[0]
            mgmtInterface.dns_preferred = dns_preferred
            mgmtInterface.dns_alternate = dns_alternate
            self.handle.set_mo(mgmtInterface)
            print '- preferred DNS server configured with IP address: ' + str(dns_preferred)
            print '- alternate DNS server configured with IP address: ' + str(dns_alternate)
        except Exception as e:
            print '- something went wrong with setting the DNS server(s): ' + str(e)
            return

    def setNTP(self, primary_ntp=None, secondary_ntp=None):
        try:
            ntp = self.handle.query_classid('CommNtpProvider')[0]
            ntp.ntp_enable = 'yes'
            ntp.ntp_server1 = primary_ntp
            ntp.ntp_server2 = secondary_ntp
            self.handle.set_mo(ntp)
            print '- primary NTP server configured with IP address: ' + str(primary_ntp)
            print '- secondary NTP server configured with IP address: ' + str(secondary_ntp)
        except Exception as e:
            print '- something went wrong with setting the NTP server(s): ' + str(e)
            return

    def setHostname(self, hostname):
        try:
            mgmtInterface = self.handle.query_classid('MgmtIf')[0]
            mgmtInterface.hostname = hostname
            self.handle.set_mo(mgmtInterface)
            print '- hostname configured as: ' + hostname
        except Exception as e:
            print '- something went wrong with setting the hostname: ' + str(e)
            return

    def generateNewSelfSignedCertificate(self):
        pass

    def setNicMode(self):
        try:
            mgmtInterface = self.handle.query_classid('MgmtIf')[0]
            mgmtInterface.nic_mode = 'dedicated'
            mgmtInterface.nic_redundancy = 'none'
            mgmtInterface.auto_neg = 'Enabled'
            self.handle.set_mo(mgmtInterface)
            print '- NIC configured as dedicated, redundancy to none and duplex and speed to auto'
        except Exception as e:
            print '- something went wrong with setting the Nic Mode: ' + str(e)
            return

    def setSNMP(self, port, community, sysContact, sysLocation, trapCommunity, trapDest, id):
        snmp = self.handle.query_classid('CommSnmp')[0]
        try:
            snmp.admin_state = 'enabled'
            snmp.port = port
            snmp.community = community
            snmp.com2_sec = 'full'
            snmp.sys_contact = sysContact
            snmp.sys_location = sysLocation
            snmp.trap_community = trapCommunity
            self.handle.set_mo(snmp)
            print '- SNMP configuration completed with the current settings:'
            print '   - admin state:     ' + snmp.admin_state
            print '   - port:            ' + snmp.port
            print '   - community:       ' + snmp.community
            print '   - com2_sec:        ' + snmp.com2_sec
            print '   - system contact:  ' + snmp.sys_contact
            print '   - system location: ' + snmp.sys_location
            print '   - trap community:  ' + snmp.trap_community
        except Exception as e:
            print '- something went wrong with setting the SNMP configuration: ' + str(e)
            return
        try:
            snmpTrap = CommSnmpTrap(snmp,
                                    id,
                                    admin_state='Enabled',
                                    version='v2c',
                                    hostname=trapDest,
                                    notification_type='traps')
            self.handle.set_mo(snmpTrap)
            print '- SNMP Trap configuration set to:'
            print '   - admin state:       Enable'
            print '   - version:           v2c'
            print '   - trap destination:  ' + trapDest
            print '   - notification_type: traps'
        except Exception as e:
            print '- something went wrong with setting the SNMP configuration: ' + str(e)
            return

    def setSyslog(self, ipAddress, name):
        try:
            syslogParent = self.handle.query_classid('CommSyslog')[0]
            syslogParent.remote_severity = 'debug'
            self.handle.set_mo(syslogParent)
            print '- syslog configured with the following parameters:'
            print '   - logging level: debug'
        except Exception as e:
            print '- something went wrong with setting the syslog logging level: ' + str(e)
            return

        try:
            syslog = CommSyslogClient(None,
                                      hostname=ipAddress,
                                      admin_state='Enabled',
                                      name=name,
                                      dn='sys/svc-ext/syslog/client-' + name)
            self.handle.set_mo(syslog)
            print '   - hostname:    ' + ipAddress
            print '   - admin state: Enabled'
            print '   - name:        ' + name
        except Exception as e:
            print '- something went wrong with setting the general syslog configuration: ' + str(e)
            return

    def setPowerPolicy(self):
        try:
            powerPolicy = self.handle.query_classid('BiosVfResumeOnACPowerLoss')[0]
            powerPolicy.vp_resume_on_ac_power_loss = 'reset'
            self.handle.set_mo(powerPolicy)
            print '- power policy set to reset'
        except Exception as e:
            print '- something went wrong with setting the power policy: ' + str(e)
            return

    def setFanPolicy(self):
        try:
            fanPolicy = self.handle.query_classid('FanPolicy')[0]
            fanPolicy.configured_fan_policy = 'Performance'
            self.handle.set_mo(fanPolicy)
            print('- fan policy set to performance')
        except Exception as e:
            print '- something went wrong with setting the fan policy: ' + str(e)
            return

    def powerOnServer(self):
        try:
            server_power_up(self.handle)
            print '- server is turned on'
        except Exception as e:
            print '- something went wrong with setting the fan policy: ' + str(e)
            return

    def setRAID1(self):
        listOfDisks = []
        storageCapacityInMB = 0
        numberOfDiskDrives = 0
        try:
            disks = self.handle.query_classid('StorageLocalDisk')
            for disk in disks:
                if disk.pd_status == 'Unconfigured Good':
                    print '- disk: ' + disk.dn + ' is already configured'
                elif disk.pd_status == 'Online':
                    print '- no changes can be made to disk ' + disk.dn + ' as long as it is already active'
                    print '- also, no logical disk can be made'
                    return
                else:
                    disk.admin_action = 'make-unconfigured-good'
                    self.handle.set_mo(disk)
                    print '- HDD: ' + disk.dn + ' has gotten its JBOD configuration removed'
                listOfDisks.append(disk.dn.split('pd-')[1])
                storageCapacityInMB = storageCapacityInMB + int(disk.coerced_size.split(' ')[0])
                numberOfDiskDrives = numberOfDiskDrives + 1
        except Exception as e:
            print '- something went wrong with setting HDD(s) in the proper mode: ' + str(e)
            return

        if numberOfDiskDrives != 0:
            storageCapacityWithRAID1 = storageCapacityInMB / 2
            storageCapacityWithRAID1 = int(storageCapacityWithRAID1)
            stringstorageCapacityWithRAID1 = str(storageCapacityWithRAID1) + 'MB'
        elif numberOfDiskDrives % 2 != 0:
            print '- please insert an even number of disks'
            return

        else:
            print '- no available disks were found'
            return

        try:
            dn = 'sys/rack-unit-1/board/storage-SAS-SLOT-HBA/virtual-drive-create'
            myStringListOfDisks = '[' + ','.join(listOfDisks) + ']'
            logicalDisk = StorageVirtualDriveCreatorUsingUnusedPhysicalDrive(None,
                                                                             raid_level='1',
                                                                             virtual_drive_name='RAID1',
                                                                             drive_group=myStringListOfDisks,
                                                                             size=stringstorageCapacityWithRAID1,
                                                                             admin_state='trigger',
                                                                             dn=dn)
            self.handle.set_mo(logicalDisk)
            print '- creating a logical disk with RAID1 and a capazity of ' + stringstorageCapacityWithRAID1
        except Exception as e:
            print '- something went wrong with setting RAID on the HDD(s): ' + str(e)
            return

    def setBootDriveAndInitialize(self):
        try:
            virtualDisk = self.handle.query_classid('StorageVirtualDrive')[0]
            virtualDisk.admin_action = 'set-boot-drive'
            self.handle.set_mo(virtualDisk)
            print '- setting boot drive'
        except Exception as e:
            print '- something went wrong with setting the boot drive: ' + str(e)
            return
        try:
            virtualDisk.admin_action = 'start-fast-initialization'
            self.handle.set_mo(virtualDisk)
            print '- initializing virtual drive'
        except Exception as e:
            print '- something went wrong with setting initialization: ' + str(e)
            return

    def setBootOrder(self):
        self._set_boot_order(self.handle, device_list=['hdd', 'pxe'])

    def _set_boot_order(self, handle, device_list=None):
        BOOT_DEVICE_MAPPING = {
            'hdd': 'HDDBOOT',
            'iscsi': 'ISCSIBOOT',
            'pchstorage': 'PCHSTORAGEBOOT',
            'pxe': 'PXEBOOT',
            'san': 'SANBOOT',
            'sdcard': 'FLEXFLASH',
            'uefishell': 'EFISHELL',
            'usb': 'USBBOOT',
            'cimc-mapped-dvd': 'CIMCDVD',
            'cimc-mapped-hdd': 'CIMCHDD',
            'kvm-mapped-dvd': 'KVMDVD',
            'kvm-mapped-hdd': 'KVMHDD',
            'kvm-mapped-fdd': 'KVMFDD',
        }

        boot_devices = []
        if device_list is None:
            device_list = []
        idx = 1

        for d in device_list:
            dev = {}
            dev['order'] = str(idx)
            dev['name'] = BOOT_DEVICE_MAPPING[d]
            if re.match('kvm|cimc', d):
                dev['subtype'] = d
                dev['device-type'] = 'vmedia'
            else:
                dev['device-type'] = d
            boot_devices.append(dev)
            idx += 1

        try:
            boot_order_precision_set(handle, reapply='yes', boot_devices=boot_devices)
            print ' - setting boot order to: '
            for device in boot_devices:
                print '   -',device['order'],device['device-type'],'with name:',device['name']
        except Exception as e:
            print '- something went wrong with setting boot order: ' + str(e)
            return

    def logout(self):
        try:
            self.handle.logout()
            print '- logged out'
        except Exception as e:
            print '- logging out of the IMC did not work as expected with the following error message: '+str(e)


