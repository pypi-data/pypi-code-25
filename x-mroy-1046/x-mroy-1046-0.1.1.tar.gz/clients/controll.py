import os
import sys
import argparse
import getpass

from fabric.api import execute, put, get, run, parallel
from fabric.api import env
from fabric.api import prompt
from fabric.contrib.files import exists
from io import BytesIO
from fabric.api import get
from qlib.data import Cache, dbobj

local_pub = open(os.getenv("HOME") + "/.ssh/id_rsa.pub").read()

class Host(dbobj):
    def patch(self):
        global env
        env.passwords[self.user + "@" + self.host + ":" + self.port] = self.passwd
        if self.host not in env.hosts:
            env.hosts.append(self.user + "@" + self.host+ ":" + self.port)

    def display(self):
        print(self.user + "@" + self.host + ":" + self.port + " ---> " + self.passwd)

SEED_HOME = os.path.join(os.getenv("HOME"), "seed")
if not os.path.exists(SEED_HOME):
    os.mkdir(SEED_HOME)
hosts_db = Cache(os.path.join(SEED_HOME, "cache.db"))

def add_host(host,port=22, user='root'):
    passwd = getpass.getpass()
    h = Host(host=host, passwd=passwd, port=port, user=user)
    h.save(hosts_db)


@parallel
def ssh_key():
    fd = BytesIO()
    if not exists("/root/.ssh/id_rsa.pub"):
        run("ssh-keygen -t rsa -P '' -f '/root/.ssh/id_rsa'")
    get("/root/.ssh/id_rsa.pub", fd)
    content=fd.getvalue()
    return content.decode()

@parallel
def upload_pub_key(key_bytes):
    put(BytesIO(key_bytes), "/root/.ssh/authorized_keys.bak", mode='0644')
    run("cat /root/.ssh/authorized_keys >> /root/.ssh/authorized_keys.bak")
    run("sort /root/.ssh/authorized_keys.bak | uniq  > /root/.ssh/authorized_keys")

@parallel
def ex(cmd):
    run(cmd)

def upload_local_pub():
    put(BytesIO(local_pub.encode()), "/root/.ssh/authorized_keys.bak")
    run("cat /root/.ssh/authorized_keys.bak >> /root/.ssh/authorized_keys")

def exchange_ssh_key(*servers):
    env.hosts += servers
    ssh = execute(ssh_key)
    authorized_keys = '\n'.join(list(ssh.values()) + [local_pub] ).encode('utf8')
    execute(upload_pub_key, authorized_keys)

@parallel
def initenv():
    sh = """
#!/bin/bash
#install python

hash apt 2>/dev/null
if [ $? -eq 0 ];then
    echo "apt is existed install apt-lib"
    apt-get install -y libc6-dev gcc
    apt-get install -y make build-essential libssl-dev zlib1g-dev libreadline-dev libsqlite3-dev wget curl llvm
else
    hash yum 2>/dev/null
    if [ $? -eq 0 ];then
        echo "yum is existed install yum-lib"
        yum -y install wget gcc make
        yum -y install zlib1g-dev bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
    fi
fi


hash python3 2>/dev/null
    if  [ $? -eq 0 ];then
    res=$(python3 -V 2>&1 | awk '{print $1}')
    version=$(python3 -V 2>&1 | awk '{print $2}')
    #echo "check command(python) available resutls are: $res"
    if [ "$res" == "Python" ];then
        if   [ "${version:0:3}" == "3.6" ];then
            echo "Command python3 could be used already."
            exit 0
        fi
    fi
fi

echo "command python can't be used.start installing python3.6."
wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
tar -zxvf Python-3.6.1.tgz
cd Python-3.6.1
mkdir /usr/local/python3
./configure --prefix=/usr/local/python3
make
make install
ln -s /usr/local/python3/bin/python3 /usr/bin/python3
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
echo 'export PATH="$PATH:/usr/local/python3/bin"' >> ~/.bashrc"""
    with open("/tmp/ini.sh", "w") as fp: fp.write(sh)
    put("/tmp/ini.sh", "/tmp/init.sh")
    run("bash /tmp/init.sh")
    run("pip3 install x-mroy-1046")

@parallel
def Startup(arg):
    if arg=='start':
        run('x-relay start')
        run('x-bak start')

    elif arg == 'stop':
        run('x-relay stop')
        run('x-bak stop')
    elif arg == 'restart':
        run('x-relay restart')
        run('x-bak restart')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a","--add-host", default=False, action='store_true', help='add a host to db')
    parser.add_argument("-s","--search", default=None, help="search local's db ")
    parser.add_argument("-d","--delete", default=False, action='store_true', help='if -s xxx -d will delete content')
    parser.add_argument("-I","--init-env", default=False, action='store_true', help='if true, will exchange_ssh_key and check then build some base env')
    parser.add_argument("-e","--execute", nargs="*", default=None, help="run some command in server")
    parser.add_argument("-S","--startup", default=None, help="start | restart | stop")

    args = parser.parse_args()
    if args.add_host:
        host = prompt("host=",default=None)
        if not host:
            print("must be a valid host")
            sys.exit(0)
        port = prompt("port=",default="22")
        user = prompt("user=",default="root")
        add_host(host,port=port,user=user)

        sys.exit(0)

    if args.search:
        hs = []
        for host in hosts_db.query(Host):
            if args.search in host.host:
                host.display()
                hs.append(host)

        if args.delete:
            for h in hs:
                hosts_db.delete(h)
        elif args.startup:
            for h in hs:
                h.patch()
            execute(Startup, args.startup)
        sys.exit(0)

    if args.init_env:
        [h.patch() for h in hosts_db.query(Host)]
        execute(initenv)
        exchange_ssh_key()
        sys.exit(0)

    if args.startup:
        w = prompt("startup op: {} all?[y/n]".format(args.startup), default='n')
        if w != 'y':
            return
        [h.patch() for h in hosts_db.query(Host)]
        execute(Startup, args.startup)

    if args.execute:
        [h.patch() for h in hosts_db.query(Host)]
        execute(ex, ' '.join(args.execute))
