import xmlrpclib
def __init__(self, client, session):
    self.session = session
    self.client = client

def listActivationKeys(self, pid):
    return self.client.system.listActivationKeys(self.session, sid)

@property
def listActiveSystems(self):
    return self.client.system.listActiveSystems(self.session)

def listActiveSystemsDetails(self, *args):
    return self.client.system.listActiveSystemsDetails(self.session, args)
@property
def listSystems(self):
    return self.client.system.listSystems(self.session)

def listSystemsWithPackage(self, pid):
    return self.client.system.listSystemsWithPackage(self.session, pid)
