'''
    About tomcat manager
'''
import os
from .pm import *

DEFAULTPATH = '/usr/local/services'


def find_tomcat():
    _, dirs, _ = os.walk(DEFAULTPATH)
    for d in dirs:
        if 'tomcat' in d:
            yield d


class Tomcat:

    def __init__(self, rootdir=DEFAULTPATH, name='tomcat', port=8080):
        self.basedir = os.path.join(rootdir, name)
        self.name = name
        self.port = port

    def getpid(self):
        pids = getpids(self.name)
        if len(pids) >= 1:
            return pids[0]
        return 0

    def getproc(self):
        p = self.getpid()
        if p:
            return Process(p)
        else:
            return None

    def status(self):
        proc = self.getproc()
        if not proc:
            dic = {'status': 'dead'}
            return dic
        net_dic = {}
        dic = {}

        conns = net_connections('tcp')
        conns_local = [i for i in conns if i.laddr[1] == self.port]
        conn_types = {key: value for key,
                      value in globals().items() if key.startswith('CONN_')}
        for key, value in conn_types.items():
            foo = [i for i in conns_local if i.status == value]
            net_dic[key[5:]] = len(foo)

        with proc.oneshot():

            if [i for i in conns if i.status == CONN_LISTEN and i.laddr[1] == self.port]:
                dic['status'] = 'open'
            else:
                dic['status'] = 'closed'

            foo = proc.memory_info().rss
            dic['drs'] = '%.2fMB' % (foo / (1024 * 1024))
            dic['cpu'] = '%s%%' % proc.cpu_percent()
        dic['conns'] = net_dic
        return dic

    def stop(self):
        if self.getpid():
            foo = os.path.join(self.basedir, 'bin/shutdown.sh')
            lxrun(['bash', foo])

    def start(self):
        foo = os.path.join(self.basedir, 'bin/startup.sh')
        lxrun(['bash', foo])

    def restart(self):
        self.stop()
        for i in range(10):
            if self.getpid():
                time.sleep(1)
            else:
                break
        self.start()
