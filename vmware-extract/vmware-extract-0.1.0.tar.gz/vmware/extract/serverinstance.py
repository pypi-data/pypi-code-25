from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
import time
import datetime
from dateutil.relativedelta import relativedelta

class ServerInstance:

    def __init__(self, vserver, user, password):
        self._vserver = vserver
        self._user = user
        self._password = password
        self._port = int(443)
        self._si = SmartConnectNoSSL(host=self._vserver,user=self._user,pwd=self._password, port=self._port)
        self._content = self._si.RetrieveContent()

    def _get_service_instance(self):
        """
            Get the service intannce by connecting to vsphere server
        """
        return self._si

    def _get_content(self):
        """
            Get the content from service instance
        """
        return self._content

    def _get_obj(self, vimtype, name):
        """
        Get the vsphere object associated with a given text name
        """
        obj = None
        container = self._si.RetrieveContent().viewManager.CreateContainerView(self._si.RetrieveContent().rootFolder, vimtype, True)
        for c in container.view:
            if c.name == name:
                obj = c
                break
        return obj

    def _get_all_objs(self, vimtype):
        """
        Get all the vsphere objects associated with a given type
        """
        obj = {}
        container = self._si.RetrieveContent().viewManager.CreateContainerView(self._si.RetrieveContent().rootFolder, vimtype, True)
        for c in container.view:
            obj.update({c: c.name})
        return obj

    def _get_all_me_objs(self, entityname):
        """
        Get all the vsphere objects associated with a given type
        """
        obj = {}
        container = self._si.RetrieveContent().viewManager.CreateContainerView(self._si.RetrieveContent().rootFolder, [vim.ManagedEntity], True)
        for c in container.view:
            if entityname in str(c):
                print c, '----', c.name
                obj.update({c: c.name})
        return obj

    def login_in_guest(username, password):
        return vim.vm.guest.NamePasswordAuthentication(username=username,password=password)

    def start_process(self, vm, auth, program_path, args=None, env=None, cwd=None):
        cmdspec = vim.vm.guest.ProcessManager.ProgramSpec(arguments=args, programPath=program_path, envVariables=env, workingDirectory=cwd)
        cmdpid = self._si.content.guestOperationsManager.processManager.StartProgramInGuest(vm=vm, auth=auth, spec=cmdspec)
        return cmdpid

    def is_ready(vm):

        while True:
            system_ready = vm.guest.guestOperationsReady
            system_state = vm.guest.guestState
            system_uptime = vm.summary.quickStats.uptimeSeconds
            if system_ready and system_state == 'running' and system_uptime > 90:
                break
            time.sleep(10)

    def get_vm_by_name(self, name):
        """
        Find a virtual machine by it's name and return it
        """
        return self._get_obj([vim.VirtualMachine], name)

    def get_host_by_name(self, name):
        """
        Find a virtual machine by it's name and return it
        """
        return self._get_obj([vim.HostSystem], name)

    def get_resource_pool(self, name):
        """
        Find a virtual machine by it's name and return it
        """
        return self._get_obj([vim.ResourcePool], name)

    def get_resource_pools(self):
        """
        Returns all resource pools
        """
        return self._get_all_objs([vim.ResourcePool])

    def get_datastores(self):
        """
        Returns all datastores
        """
        return self._get_all_objs([vim.Datastore])

    def get_hosts(self):
        """
        Returns all hosts
        """
        return self._get_all_objs([vim.HostSystem])

    def get_datacenters(self):
        """
        Returns all datacenters
        """
        return self._get_all_objs([vim.Datacenter])

    def get_registered_vms(self):
        """
        Returns all vms
        """
        return self._get_all_objs([vim.VirtualMachine])

    # Below are for managed entity (me)
    def get_me_resource_pool(self, name):
        """
        Find a virtual machine by it's name and return it
        """
        return self._get_obj([vim.ManagedEntity], name)

    def get_me_resource_pools(self):
        """
        Returns all resource pools
        """
        return self._get_all_me_objs("ResourcePool")

    def get_me_datastores(self):
        """
        Returns all datastores
        """
        return self._get_all_me_objs("Datastore")

    def get_me_hosts(self):
        """
        Returns all hosts
        """
        return self._get_all_me_objs([vim.HostSystem])

    def get_me_datacenters(self):
        """
        Returns all datacenters
        """
        return self._get_all_me_objs("Datacenter")

    def get_me_registered_vms(self):
        """
        Returns all vms
        """
        return self._get_all_me_objs("VirtualMachine")

    def get_performance_manager(self):
        """
        Returns Performance manager object
        """
        return self._get_content().perfManager

    def get_available_performance_metric(self, vm):
        """
        Returns Available Performance Metric
        """
        return self.get_performance_manager().QueryAvailablePerfMetric(entity=vm)

    def get_metric_ID(self, counterID):
        """
        Returns metric ID for given counter ID
        """
        return vim.PerformanceManager.MetricId(counterId=counterID, instance="*")

    def get_query_spec(self, start_time, vm, metricIDs):
        """
        Returns Query Spec
        """
        return vim.PerformanceManager.QuerySpec(startTime=start_time,
                                            endTime = start_time + relativedelta(months=1),
                                            entity=vm,
                                            metricId = metricIDs,
                                            intervalId=7200,
                                            format="csv")

    def get_metric(self, speclist):
        """
        Return Metric Results
        """
        return self.get_performance_manager().QueryStats(querySpec=speclist)

    def get_performance_provider_summary(self, vm):
        """
        Return Metric Results
        """
        return self.get_performance_manager().QueryPerfProviderSummary(entity=vm)

