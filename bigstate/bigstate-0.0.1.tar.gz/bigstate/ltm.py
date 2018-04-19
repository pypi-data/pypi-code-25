from f5.bigip import ManagementRoot
import logging
import re
import requests

class ltm():

  def sync(sync_group):
    mgmt.tm.cm.exec_cmd('run', utilCmdArgs='config-sync to-group {}'.format(sync_group))

  def __init__(self, f5ManagementRoot, partition = "Common"):
    #if f5ManagementRoot.tmos_version.split(".")[0] < 12:
    #  raise Exception("TMOS version must be at >=12.0.0")
    #else:
    self.partition = partition
    self.connection = f5ManagementRoot
    self.ltm = f5ManagementRoot.tm.ltm

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

  ## Node Related Functions ##
  def _delete_node(self, name):
    pass

  def node_matches(self, name, address, options, partition = None):
    ''' ensure the node exists and is configured as specified
        or creates a new one
    '''
    partition = partition if partition else self.partition
    if self.ltm.nodes.node.exists(name = name, partition = partition):
      node = self.ltm.nodes.node.load(name = name, partition = partition)
      if not self._compare_resources(node.attrs, options):
        node.update(**options)
        if not self._compare_resources(node.attrs, options): return False
      if address and node.address != address: return False
    else:
      node = self.ltm.nodes.node.create(name = name, address = address, partition = partition, **options)
      return node.exists(name = node.name, partition = node.partition)

  ## Pool Related Functions ##
  def _add_pool_member(self, pool, member, partition):
    mpartition = partition if partition not in member else member['partition']
    mname = "{}:{}".format(member['name'], member['port'])
    options = {} if 'options' not in member else member['options']
    partition = partition if 'partition' not in member else member['partition']
    m = pool.members_s.members.create(name = mname, partition = partition, **options)
    return m.exists(name = m.name, partition = m.partition)

  def pool_matches(self, name, options = {}, members = [], partition = "Common"):
    partition = partition if partition else self.partition
    ''' ensure the pool exists and is configured as specified
        or create a new one
    '''
    if self.ltm.pools.pool.exists(name = name, partition = partition):
      pool = self.ltm.pools.pool.load(name = name, partition = partition)
      if not self._compare_resources(pool.attrs, options):
        pool.update(**options)
        if not self._compare_resources(pool.attrs, options): return False
      if members:
        pool_members = pool.members_s.get_collection()
        members_d = {"{}:{}".format(m['name'], m['port']):i for i, m in enumerate(members)}
        pool_members_dict = {}
        for i, member in enumerate(pool_members):
          n = member.name.strip()
          pool_members_dict[n] = i
          logging.info('checking %s', n)
          if n in members_d:
            if not 'options' in members[members_d[n]]:
              logging.info('skipping %s check no options found in config', n) 
              continue
            moptions = members[members_d[n]]['options']
            if not self._compare_resources(member.attrs, moptions):
              logging.info('updating %s to match options: %s', n, moptions)
              member.update(members[members_d[n]]['options'])
          else:
            logging.info('removing %s from %s', n, pool.name)
            member.delete()
        for m, i in members_d.items():
          logging.debug('Verifying %s in %s', m, pool.name)
          if m not in pool_members_dict:
            logging.info("adding %s to %s",m, pool.name)
            self._add_pool_member(pool, members[i], partition)
    else:
      pool = self.ltm.pools.pool.create(name = name, partition = partition, **options)
      for member in members:
        self._add_pool_member(pool, member, partition)


  ## Monitor related functions ##
  def _get_monitor_resource(self, type_name):
    mtype_name = type_name + "s" if type_name[-1] != "s" else type_name + "_s"
    mtype = getattr(self.ltm.monitor, mtype_name)
    return getattr(mtype, type_name)

  def monitor_matches(self, name, type_name, options, partition = "Common"):
    """
    Ensure monitor matches configuration as specified

    Keyword arguments:
    name -- name of monitor
    type_name -- monitor type name
    options -- monitor options as document in F5 SDK (defualt {})
    partition -- partition to search for monitor (default "Common")
    """
    partition = partition if partition else self.partition
    monitor = self._get_monitor_resource(type_name)
    if monitor.exists(name = name, partition = partition):
      if options:
        m = monitor.load(name = name, partition =partition)
        if self._compare_resources(m.attrs, options):
          return True
        else:
          m.update(**options)
          return self._compare_resources(m.attrs, options)
      else:
        return True
    else:
      m = monitor.create(name = name, type_name = type_name, partition = partition, **options)
      return m.exists(name = m.name, partition = m.name)

  ## iRule related functions ##
  def _load_rule_data(self, irule):
    if re.match('^(http|https)://', irule):
      irule = requests.get(irule).text
    elif re.match('^file://', irule):
      with open(irule[7:]) as rule_data:
        irule = rule_data.read()
    return irule

  def irule_matches(self, name, irule = "", options = {}, partition = "Common"):
    partition = partition if partition else self.partition
    if irule:
      options['apiAnonymous'] = self._load_rule_data(irule)
    if self.ltm.rules.rule.exists(name = name, partition = partition):
      if options:
        rule = self.ltm.rules.rule.load(name = name, partition = partition)
        if not self._compare_resources(rule.attrs, options):
          rule.update(options)
          rule.refresh()
          return self._compare_resources(rule.attrs, options)
    else:
      rule = self.ltm.rules.rule.create( name = name, partition = partition, **options)
      return rule.exists(name = name, partition = partition)
      
  ## Datagroup functions ##
  def _compare_dg_records(self, records, dg_records):
    records_d = {r['name']:r['data'] for r in dg_records}
    rk = records.keys()
    if rk == records_d.keys():
      for k in rk:
        if records_d[k] != records[k]: return False
      return True
    else:
      return False

  def datagroup_matches(self, name, type, records = {}, options = {}, partition = "Common", external = True):
    partition = partition if partition else self.partition
    dgrecords = [ {'name': k, 'data': v} for k,v in records.items() ]
    if self.ltm.data_group.internals.internal.exists(name = name, partition = partition):
      dg = self.ltm.data_group.internals.internal.load(name = name, partition = partition)
      noptions = {k:v for k,v in options.items() if k != 'records'}
      if not self._compare_resources(dg.attrs, noptions):
        dg.update(noptions)
        if not self._compare_resources(dg.attrs, noptions): return False
      if records:
        if not self._compare_dg_records(records, dg.records):
          dg.update(records = dgrecords)
          return self._compare_dg_records(records, dg.records)
      return True
    else:
      dg = self.ltm.data_group.internals.internal.create(name = name, type = type, records = dgrecords, partition = partition, **options)
      return dg.exists(name = name, partition = partition)

  ## Virtual Server Functions ##
  def virtual_server_matches(self, name, options = {}, partition = "Common"):
    partition = partition if partition else self.partition
    if self.ltm.virtuals.virtual.exists(name = name, partition = partition):
      virtual = self.ltm.virtuals.virtual.load(name = name, partition = partition)
      if self._compare_resources(virtual.attrs, options):
        return True
      else:
        virtual.update(**options)
        return self._compare_resources(virtual.attrs, options)
    else:
      if not 'destination' in options:
        logging.error('destination required in options to avoid accidents')
      virtual = self.ltm.virtuals.virtual.create(name = name, partition = partition, **options)
      return virtual.exists(name = name, partition = partition)
