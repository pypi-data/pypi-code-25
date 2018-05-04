#!/usr/bin/env python3
import argparse, os, sys
from mroylib.services.remote import controll
from mroylib.services.remote import fablibs
from mroylib.services.remote.fablibs import env
from qlib.data.sql import SqlEngine
from qlib.log import show, L
from cmd import Cmd
from termcolor import colored
from fabric.api import execute, settings, run
from getpass import getpass
Sql = SqlEngine(database=os.path.join(os.getenv("HOME"), "Rcontrol.conf.db"))
# if not os.path.exists(os.path.join(os.getenv("HOME"), "Rcontrol.conf.db")):
try:
    Sql.create('hosts', target=str, user='root', port='22', password=str)
except :
    pass
# env.roledefs = {str(i):['root@'+v] for i,v in enumerate(
    # [i.strip() for i in open(os.path.join(ROOT_PATH,"server.list")).readlines() if i.strip() ])}

def Chooseids(i):
    for s in  i.split("-"):
        for id in s.split(","):
            yield int(id)

class Cli(Cmd):

    def __init__(self):
        super().__init__()
        self.timestamp = ''
        self.prompt = colored("- ","red")
        self.user = 'root'
        self.port = '22'

    def do_quit(self,args):
        return True

    def do_set(self, args):
        h, f = args.split(None, 2)
        if h not in ['target', 'user', 'port', 'password']:
            show(" must in ['target', 'user', 'port', 'password']", color='red')
        setattr(self, h, f)

    def do_list(self, args):
        for i in Sql.select('hosts'):
            show(*i)

    def complete_set(self, text, line, begidx, endidx):
        for i in ['target', 'user', 'port', 'password', '192.168.']:
            if text in i:
                return [i]



    def do_show(self, args):
        for h  in ['target', 'user', 'port', 'password']:
            show(h,"=", getattr(self, h, "not set !"))

    def do_delete(self, id):
        Sql.delete('hosts', id=id)

    def do_search(self, sf):
        for i in Sql.select('hosts'):
            sho = False
            for m in i:
                if isinstance(m, str):
                    if sf in m:
                        sho = True
            if sho:
                show(i)
                break

    def do_save(self, args):
        s = True
        for k in ['target', 'user', 'port', 'password']:
            if not hasattr(self, k):
                s = k
        if s == True:
            Sql.insert("hosts", ['target', 'user', 'port', 'password'], self.target, self.user, self.port, self.password)
        else:
            show(k, "is not set !!")


def setPassword(passwd):
    global env
    fablibs.env['password'] = passwd

def load_sql(sql):
    global env
    env.roledefs = {str(i):[v[3] + "@" + v[2] + ":" + v[4] ] for i,v in enumerate(
        [v for v in sql.select("hosts")])}

    if not env.hosts:
        for i in env.roledefs:
            show(i,env.roledefs[i])
        host = input(colored(">>", "green", attrs=['underline']))
        if len(host) < 18:
            if ',' not in host:
                host_id = int(host)
                env.host = env.roledefs[str(host_id)][0]
                env.hosts = env.roledefs[str(host_id)]
            else:
                env.hosts = [ env.roledefs[i][0] for i in host.split(",")]
        show("set hosts: ", env.hosts)
    elif re.match(r'^(\d{1,3}\.){3}\d{1,3}$', host):
        env.host = 'root@' + host
        env.hosts = ['root@' + host]
        env.host_string
    else:
        show("not match!! , just save as domain host", color='yellow')

    # show(len(env.passwords))
    if len(env.passwords) ==0:
        try:
            for host in env.hosts:
                tt = host.split("@")[1].split(":")[0]
                show(host,"--==> ", color='red')
                env.passwords[host], = sql.first("hosts", 'password', target=tt)
        except AttributeError as e:
            print(e)
            passwds = None
        if not env.passwords:
            env.password = getpass()



def parse():
    arsgs = argparse.ArgumentParser(usage="controll and multi do")
    arsgs.add_argument("-d", "--db-mode", action="store_true", default=False,help="handle db")
    arsgs.add_argument("-f", "--load-servers",help="hosts' files ")
    arsgs.add_argument("-e", "--excute", nargs="*", help="Run shell!")
    arsgs.add_argument("-p", "--password",default=None, help="handle db")
    arsgs.add_argument("-u", "--upload", nargs="*",help="upload db to servers")
    arsgs.add_argument("--shadowsocks", nargs="*",help="build shadowsocks : setup or start")
    args.add_argument("-U", "--update", default=None, help="update all package: package_dir | network")
    arsgs.add_argument("--ssh", action="store_true", default=False, help="build shadowsocks : setup or start")

    return arsgs.parse_args()

def main():
    args = parse()
    if args.update:
        if args.update == 'network':
            execute(fablibs.ex, "pip3 uninstall -y x-mroy-1046 && pip3 install x-mroy-1046 --no-cache-dir ")
        elif os.path.exists(args.update):
            pass

    if args.db_mode:
        Cli().cmdloop()
        sys.exit(0)

    if args.password:
        setPassword(args.passwd)
        sys.exit(0)

    if args.load_servers:
        controll.load(args.load_servers)
    else:
        load_sql(Sql)

    if args.upload:
        for f in args.upload:
            execute(fablibs.up, f)

    if args.excute:
        # for h in env.hosts:
        #     with settings(host_string=h[0]):
        execute(fablibs.ex, " ".join(args.excute))

    if args.shadowsocks:
        stop = False
        if "stop" in args.shadowsocks:
            stop = True
        if 'setup' in args.shadowsocks:
            execute(fablibs.shadowsocks, False, stop)

        if "start" in args.shadowsocks:
            execute(fablibs.shadowsocks, True, stop)
    if args.ssh:
        execute(fablibs.keysave)

if __name__ == '__main__':
    main()
