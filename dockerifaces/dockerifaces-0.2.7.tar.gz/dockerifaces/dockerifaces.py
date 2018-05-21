import sys
import docker
from ifaceinfo import InterfacesInfos

#
# target for version 0.3
# Allow user to pass ifaceinfo (InterfacesInfos()) to the class to  skeep reloading data
#   it's good when you have to load saved json stucture of InterfacesInfos()
#   it's good when you use ifaceinfo package and dockerifaces package in the same programm
# Add vswitch how the host veth are connected and put all information in the new structure
# Collect the statistics about veth used by container
#
class DockerInterfaces():
    def __init__(self, ifaceinfo=''):
        self.__dockerClient = docker.from_env()
        # manage the ifaceinfo is provided or not
        if ifaceinfo == '':
            self.__ifaceinfoprovided = False
            self.__hostinterfaces    = InterfacesInfos()
        else:
            self.__ifaceinfoprovided = True
            self.__hostinterfaces    = ifaceinfo
        self.__hostinterfacesIndexLink = self.__hostinterfaces.ifaces_ifindex_iflink()
        self.__containersInterfaces    = self.__containers_collect_data()
        self.__ifacesinterconnected    = self.__merge_interfaces()

    def refresh(self):
        '''
        refresh data loaded if not provided
        '''
        #if self.__ifaceinfoprovided is False we can reload else we do nothing
        if not self.__ifaceinfoprovided:
            self.__init__()

    def reload(self):
        '''
        same as refresh() [alias]
        '''
        self.refresh()

    def container_ifaces_connexion(self):
        '''
        return merged structure json between ifaceinfo and the structure build from docker container.
        every object in the return result use the host ethernet network name as key of the value that reprensent the relationship
        '''
        return self.__ifacesinterconnected

    def local_ifaces_to_containers(self):
        '''
        same as container_ifaces_connexion() [alias]
        '''
        return self.container_ifaces_connexion()

    def local_ifaces_index_link(self):
        '''
        return the host interfaces network ifindex and iflink informations
        '''
        return self.__hostinterfacesIndexLink

    def containers_ifaces(self):
        '''
        return the container data collected
        '''
        return self.__containersInterfaces

    def __get_containers_by(self, param):
        '''
        private method that return containers network information by: ifindex or iflink or address or operstate provided as string param
        this method is used by:
            containers_ifaces_index()
            containers_ifaces_link()
            containers_ifaces_addrs()
            containers_ifaces_statue()
        '''
        __c_interfaces = {}
        _containeriface = self.containers_ifaces()
        for _iface in _containeriface:
            for _c_ifinfo in _containeriface[_iface]:
                if _c_ifinfo != 'name' and _c_ifinfo != 'id':
                    __c_interfaces[_iface] = {}
                    __c_interfaces[_iface][_c_ifinfo] = {
                        param: _containeriface[_iface][_c_ifinfo][param]
                    }
        return __c_interfaces

    def containers_ifaces_index(self):
        '''
        return containers interface and ifindex
        '''
        return self.__get_containers_by('ifindex')

    def containers_ifaces_link(self):
        '''
        return containers interface and iflink
        '''
        return self.__get_containers_by('iflink')

    def containers_ifaces_addrs(self):
        '''
        return containers interface and mac address
        '''
        return self.__get_containers_by('address')

    def containers_ifaces_statue(self):
        '''
        return containers interface and operstate
        '''
        return self.__get_containers_by('operstate')

    def __merge_interfaces(self):
        '''
        private method used by __init__() to merge data provided by ifaceinfo and data collected by the private method __containers_collect_data()
        '''
        __mergin = {}
        __containeriface = self.containers_ifaces()
        for containerid in __containeriface:
            for __iface in __containeriface[containerid]:
                if __iface != 'id' and __iface != 'name':
                    # name, addr, ifindex, iflink
                    __c_shortid     = containerid
                    __c_id          = __containeriface[containerid]['id']
                    __c_ifacename   = __containeriface[containerid][__iface]['name']
                    __c_ifaceaddr   = __containeriface[containerid][__iface]['address']
                    __c_ifindex     = __containeriface[containerid][__iface]['ifindex']
                    __c_iflink      = __containeriface[containerid][__iface]['iflink']
                    __c_ifoperstate = __containeriface[containerid][__iface]['operstate']
                    for __localifaces in self.local_ifaces_index_link():
                        if __localifaces['ifindex'] == __c_iflink and __localifaces['iflink'] == __c_ifindex:
                            __mergin[__localifaces['name']] = {
                                'ifindex'         : __localifaces['ifindex'],
                                'iflink'          : __localifaces['iflink'],
                                'ip'              : __localifaces['ip'],
                                'mask'            : __localifaces['mask'],
                                'name'            : __localifaces['name'],
                                'network_address' : __localifaces['network_address'],
                                'operstate'       : __localifaces['operstate'],
                                'container': {
                                    'short_id'  :__c_shortid,
                                    'address'   : __c_ifaceaddr,
                                    'ifindex'   : __c_ifindex,
                                    'iflink'    : __c_iflink,
                                    'ifacename' : __c_ifacename,
                                    'id'        : __c_id,
                                    'name'      : __iface,
                                    'operstate' : __c_ifoperstate
                                }
                            }
        return __mergin


    def __convert_value(self, valuetoconvert):
        """
        private methode that convert from string to int or float or keep string if tye is not detected
        """
        _value = ''
        try:
            _value = int(valuetoconvert)
        except ValueError:
            try:
                _value = float(valuetoconvert)
            except ValueError:
                _value = valuetoconvert
        return _value


    def __containers_collect_data(self):
        '''
        the main function that use docker python package to get data from container using exec_run() this method is called by __init__()
        '''
        __dockerClient = docker.from_env()
        _containers = __dockerClient.containers.list()
        _containersinfos = {}
        for _container in _containers:
            _containersinfos[_container.short_id] = {
                'id'   : _container.id,
                'name' : _container.name
            }
            # iface networks for this container
            _ifnetworks = _container.exec_run('ls /sys/class/net')
            if _ifnetworks.exit_code == 0:
                _ifnetworks = _ifnetworks.output.decode().split('\n')
                # now for every interface located except lo and empty string in the list
                _ifnetworks = [_iface for _iface in _ifnetworks if _iface and _iface != 'lo']
                # now get ifindex, iflink and interface physical address for every interface
                for iface in _ifnetworks:
                    _ifindex     = _container.exec_run('cat /sys/class/net/' + iface + '/ifindex')
                    _iflink      = _container.exec_run('cat /sys/class/net/' + iface + '/iflink')
                    _ifaddr      = _container.exec_run('cat /sys/class/net/' + iface + '/address')
                    _ifoperstate = _container.exec_run('cat /sys/class/net/' + iface + '/operstate')
                    _containersinfos[_container.short_id][iface] = {
                        'name'      : iface,
                        'ifindex'   : self.__convert_value(_ifindex.output.decode()) if _ifindex.exit_code == 0 else -1,
                        'iflink'    : self.__convert_value(_iflink.output.decode()) if _iflink.exit_code == 0 else -1,
                        'address'   : self.__convert_value(_ifaddr.output.decode().replace('\n', '')) if _ifaddr.exit_code == 0 else 'unknown',
                        'operstate' : self.__convert_value(_ifoperstate.output.decode().replace('\n', '')) if _ifaddr.exit_code == 0 else 'unknown'
                    }
        return _containersinfos


    def containers_ifaces_to_local_ifaces(self):
        '''
        return reversed structure json of container_ifaces_connexion() that reverse the entry point.
        every object in the return result use the container short_id as key of the value that reprensent the relationship
        '''
        # create new object __reverse_merge
        __reverse_merge = {}
        # get original data collected
        __merged = self.local_ifaces_to_containers()
        # for every local host network name do the reverse :)
        for __l_ifacename in __merged:
            # now very entry should use the short_id of container every container as key
            #
            #  ISSUE: In the case of multiple network interface in container !!! data will be false :(
            #
            __c_shortid   = __merged[__l_ifacename]['container']['short_id']
            __c_address   = __merged[__l_ifacename]['container']['address']
            __c_id        = __merged[__l_ifacename]['container']['id']
            __c_ifname    = __merged[__l_ifacename]['container']['ifacename']
            __c_ifindex   = __merged[__l_ifacename]['container']['ifindex']
            __c_iflink    = __merged[__l_ifacename]['container']['iflink']
            __c_name      = __merged[__l_ifacename]['container']['name']
            __c_operstate = __merged[__l_ifacename]['container']['operstate']
            __reverse_merge[__c_shortid] = {
                'address'       : __c_address,
                'id'            : __c_id,
                'ifacename'     : __c_ifname,
                'ifindex'       : __c_ifindex,
                'iflink'        : __c_iflink,
                'name'          : __c_name,
                'short_id'      : __c_shortid,
                'operstate'     : __c_operstate,
                'host_interface': {}
            }
            # this will manage the case of multiple network interfaces in docker container
            #__l_name = __merged[str(__c_shortid)]['host_interface'][__merged[__l_ifacename]['name']]
            #__l_name = 
            __l_ifindex     = __merged[__l_ifacename]['ifindex']
            __l_iflink      = __merged[__l_ifacename]['iflink']
            __l_ifip        = __merged[__l_ifacename]['ip']
            __l_ifmask      = __merged[__l_ifacename]['mask']
            __l_ifname      = __merged[__l_ifacename]['name']
            __l_ifnetwork   = __merged[__l_ifacename]['network_address']
            __l_ifoperstate = __merged[__l_ifacename]['operstate']
            __reverse_merge[__merged[__l_ifacename]['container']['short_id']]['host_interface'][__merged[__l_ifacename]['name']] = {
                'ifindex'        : __l_ifindex,
                'iflink'         : __l_iflink,
                'ip'             : __l_ifip,
                'mask'           : __l_ifmask,
                'name'           : __l_ifname,
                'network_address': __l_ifnetwork,
                'operstate'      : __l_ifoperstate
            }
        return __reverse_merge


