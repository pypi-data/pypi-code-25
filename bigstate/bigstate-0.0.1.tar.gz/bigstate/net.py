from f5.bigip import ManagementRoot
import logging
import re
import requests

class net():

  def sync(sync_group):
    mgmt.tm.cm.exec_cmd('run', utilCmdArgs='config-sync to-group {}'.format(sync_group))

  def __init__(self, f5ManagementRoot):
    #if f5ManagementRoot.tmos_version.split(".")[0] < 12:
    #  raise Exception("TMOS version must be at >=12.0.0")
    #else:
    self.connection = f5ManagementRoot
    self.net = f5ManagementRoot.tm.net

  ## Common utility functions
  def _compare_resources(self, attrs, options):
    # todo: add support for nested compares
    #partition = ""
    #if 'partition' in attrs:
    partition = "/{}/".format(attrs['partition'])
    for k,v in options.items():
      if not k in attrs: continue
      a = attrs[k] if type(attrs[k]) != str else attrs[k].strip()
      if a == v or a == "/Common/"+str(v) or a == partition+str(v): continue
      else:
        logging.info("attribute: %s needs to be updated from %s to %s",k , a, v)
        return False
    return True

  ## Self IP Functions ##
  def selfip_matches(self, name, address, vlan, options = {}, partition = "Common"):
    if self.net.selfips.selfip.exists(name = name, partition = partition):
      selfip = self.net.selfips.selfip.load(name = name, partition = partition)
      if self._compare_resources(selfip.attrs, options):
        return True
      else:
        selfip.update(**options)
        return self._compare_resources(selfip.attrs, options)
    else:
      selfip = self.net.selfips.selfip.create(name = name, address = address, vlan = vlan, partition = partition, **options)
      return selfip.exists(name = name, partition = partition)
