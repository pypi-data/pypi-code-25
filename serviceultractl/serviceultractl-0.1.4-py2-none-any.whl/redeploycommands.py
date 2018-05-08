# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.service import ServiceDispatch as Service


class RedeployCommands(object):
    @args("--serviceid", dest="serviceids", required=True, nargs="+", help="")
    @args("--appid", dest="appid", required=True, help="")
    def service(self, auth, serviceids, appid):
        """redeploy service"""
        Service.redeploy_batch(auth, appid, serviceids)


