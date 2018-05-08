# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.commonnode import CommonNodeDispatch as CN
from .v3_0.service import ServiceDispatch as Service
from .v3_0.task import TaskDispatch as Task
from .v3_0.instance import InstanceDispatch as Instance


class UndeployCommands(object):
    @args("--machineid", dest="machineids", required=True, nargs="+", help="")
    @args("--clusterid", dest="clusterid", required=True, help="")
    def machine(self, auth, machineids, clusterid):
        """undeploy machine"""
        CN.undeploy_batch(auth, clusterid, machineids)

    @args("--serviceid", dest="serviceids", required=True, nargs="+", help="")
    @args("--appid", dest="appid", required=True, help="")
    def service(self, auth, serviceids, appid):
        """undeploy service"""
        Service.undeploy_batch(auth, appid, serviceids)

    @args("--instanceid", dest="instanceids", required=True, nargs="+", help="")
    @args("--microserviceid", dest="microserviceid", required=True, help="")
    @args("--serviceid", dest="serviceid", required=True, help="")
    def instance(self, auth, instanceids, microserviceid, serviceid):
        """undeploy instance"""
        Instance.undeploy_batch(auth, serviceid, microserviceid, instanceids)

    @args("--taskid", dest="taskids", required=True, nargs="+", help="")
    @args("--appid", dest="appid", required=True, help="")
    def task(self, auth, taskids, appid):
        """undeploy task"""
        Task.undeploy_batch(auth, appid, taskids)
