import sys
import docker
from ifaceinfo import InterfacesInfos
from pprint import pprint


class DockerInterfaces():
    def __init__(self):
        self.__dockerClient = docker.from_env()
        self.__hostinterfaces = InterfacesInfos()
        self.__hostinterfacesIndexLink = self.__hostinterfaces.ifaces_ifindex_iflink()
        self.__containersInterfaces = self.__containers_collect_data()
        self.__ifacesinterconnected = self.__merge_interfaces()
    
    def container_ifaces_connexion(self):
        return self.__ifacesinterconnected

    def local_ifaces_to_containers(self):
        return self.container_ifaces_connexion()

    def containers_ifaces_to_local_ifaces(self):
        __reverse_merge = {}
        __merged = self.local_ifaces_to_containers()
        for __l_ifacename in __merged:
            __reverse_merge[__merged[__l_ifacename]['container']['short_id']] = {
                'address': __merged[__l_ifacename]['container']['address'],
                'id': __merged[__l_ifacename]['container']['id'],
                'ifacename': __merged[__l_ifacename]['container']['ifacename'],
                'ifindex': __merged[__l_ifacename]['container']['ifindex'],
                'iflink': __merged[__l_ifacename]['container']['iflink'],
                'name': __merged[__l_ifacename]['container']['name'],
                'short_id': __merged[__l_ifacename]['container']['short_id'],
                'operstate': __merged[__l_ifacename]['container']['operstate'],
                'host_interface': {
                    'ifindex': __merged[__l_ifacename]['ifindex'],
                    'iflink': __merged[__l_ifacename]['iflink'],
                    'ip': __merged[__l_ifacename]['ip'],
                    'mask': __merged[__l_ifacename]['mask'],
                    'name': __merged[__l_ifacename]['name'],
                    'network_address': __merged[__l_ifacename]['network_address'],
                    'operstate': __merged[__l_ifacename]['operstate']
                }
            }
        return __reverse_merge

    def refresh(self):
        self.__init__()

    def reload(self):
        self.refresh()

    def local_ifaces_index_link(self):
        return self.__hostinterfacesIndexLink

    def containers_ifaces(self):
        return self.__containersInterfaces

    def __get_containers_by(self, param):
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
        return self.__get_containers_by('ifindex')

    def containers_ifaces_link(self):
        return self.__get_containers_by('iflink')

    def containers_ifaces_addrs(self):
        return self.__get_containers_by('address')

    def containers_ifaces_statue(self):
        return self.__get_containers_by('operstate')

    def __merge_interfaces(self):
        __mergin = {}
        __containeriface = self.containers_ifaces()
        for containerid in __containeriface:
            print(containerid)
            for __iface in __containeriface[containerid]:
                if __iface != 'id' and __iface != 'name':
                    # name, addr, ifindex, iflink
                    __c_shortid = containerid
                    __c_id = __containeriface[containerid]['id']
                    __c_ifacename = __containeriface[containerid][__iface]['name']
                    __c_ifaceaddr = __containeriface[containerid][__iface]['address']
                    __c_ifindex = __containeriface[containerid][__iface]['ifindex']
                    __c_iflink = __containeriface[containerid][__iface]['iflink']
                    __c_ifoperstate = __containeriface[containerid][__iface]['operstate']
                    for __localifaces in self.local_ifaces_index_link():
                        if __localifaces['ifindex'] == __c_iflink and __localifaces['iflink'] == __c_ifindex:
                            pprint(__localifaces)
                            __mergin[__localifaces['name']] = {
                                'ifindex': __localifaces['ifindex'],
                                'iflink': __localifaces['iflink'],
                                'ip': __localifaces['ip'],
                                'mask': __localifaces['mask'],
                                'name': __localifaces['name'],
                                'network_address': __localifaces['network_address'],
                                'operstate': __localifaces['operstate'],
                                'container': {
                                    'short_id':__c_shortid,
                                    'address': __c_ifaceaddr,
                                    'ifindex': __c_ifindex,
                                    'iflink': __c_iflink,
                                    'ifacename': __c_ifacename,
                                    'id': __c_id,
                                    'name': __iface,
                                    'operstate': __c_ifoperstate
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
        __dockerClient = docker.from_env()
        _containers = __dockerClient.containers.list()
        _containersinfos = {}
        for _container in _containers:
            _containersinfos[_container.short_id] = {
                'id': _container.id,
                'name': _container.name
            }
            # iface networks for this container
            _ifnetworks = _container.exec_run('ls /sys/class/net')
            if _ifnetworks.exit_code == 0:
                _ifnetworks = _ifnetworks.output.decode().split('\n')
                # now for every interface located except lo and empty string in the list
                _ifnetworks = [_iface for _iface in _ifnetworks if _iface and _iface != 'lo']
                # now get ifindex, iflink and interface physical address for every interface
                for iface in _ifnetworks:
                    _ifindex = _container.exec_run('cat /sys/class/net/' + iface + '/ifindex')
                    _iflink = _container.exec_run('cat /sys/class/net/' + iface + '/iflink')
                    _ifaddr = _container.exec_run('cat /sys/class/net/' + iface + '/address')
                    _ifoperstate = _container.exec_run('cat /sys/class/net/' + iface + '/operstate')
                    _containersinfos[_container.short_id][iface] = {
                        'name': iface,
                        'ifindex': self.__convert_value(_ifindex.output.decode()) if _ifindex.exit_code == 0 else -1,
                        'iflink': self.__convert_value(_iflink.output.decode()) if _iflink.exit_code == 0 else -1,
                        'address': self.__convert_value(_ifaddr.output.decode().replace('\n', '')) if _ifaddr.exit_code == 0 else 'unknown',
                        'operstate' : self.__convert_value(_ifoperstate.output.decode().replace('\n', '')) if _ifaddr.exit_code == 0 else 'unknown'
                    }
        return _containersinfos





