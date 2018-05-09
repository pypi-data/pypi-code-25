import os
import sys
import argparse
import getpass
import zipfile

from fabric.api import execute, put, get, run, parallel
from fabric.api import env
from fabric.api import prompt
from fabric.contrib.files import exists
from io import BytesIO
from fabric.api import get
from qlib.data import Cache, dbobj
from qlib.log import L
from functools import partial
from fabric.colors import red, green, blue
from base64 import b64encode
from functools import partial
from seed.mrpackage.test import Test
from seed.mrpackage.config import SEED_HOME
from seed.mrpackage.config import DB_PATH, LOCAL_PUB_KEY
from seed.mrpackage.config import Host,Cache

local_pub = open(LOCAL_PUB_KEY).read()
PY3_ENV = 'export PATH="$PATH:/usr/local/python3/bin" && '
srun = run
class FixProgress:
    def __init__(self):
        self.saw_progress = False
        self.last =''

    def write(self, s):
        if '%' in s:
            s = s.strip()
            print(s,end='\r')

        else:
            if s.strip():
                print(s, end='')
            else:
                pass

    def flush(self):
        sys.stdout.flush()

run = partial(run, stdout=FixProgress())
env.output_prefix = False

hosts_db = Cache(DB_PATH)

def add_host(host,port=22, user='root'):
    passwd = getpass.getpass()
    h = Host(host=host, passwd=passwd, port=port, user=user)
    h.save(hosts_db)

@parallel
def backup():
    pass

@parallel
def ssh_key():
    fd = BytesIO()
    if not exists("/root/.ssh/"):
        run("mkdir -p /root/.ssh/ && ssh-keygen -t rsa -P '' -f /root/.ssh/id_rsa")
    if not exists("/root/.ssh/id_rsa.pub"):
        run("ssh-keygen -t rsa -P '' -f '/root/.ssh/id_rsa'")
    get("/root/.ssh/id_rsa.pub", fd)
    content=fd.getvalue()
    return content.decode()

@parallel
def upload_pub_key(key_bytes):
    if not exists("/root/.ssh/authorized_keys"):
        run("touch /root/.ssh/authorized_keys")

    put(BytesIO(key_bytes), "/root/.ssh/authorized_keys.bak", mode='0644')
    run("cat /root/.ssh/authorized_keys >> /root/.ssh/authorized_keys.bak")
    run("sort /root/.ssh/authorized_keys.bak | uniq  > /root/.ssh/authorized_keys")

@parallel
def ex(cmd):
    res = run(PY3_ENV +  cmd,quiet=True)
    print(green("[+]"),blue(env.host), cmd)
    print(blue("[{}]".format(env.host)), res)

@parallel
def exd(cmd):
    run(PY3_ENV + cmd)

def upload_local_pub():
    put(BytesIO(local_pub.encode()), "/root/.ssh/authorized_keys.bak")
    run("cat /root/.ssh/authorized_keys.bak >> /root/.ssh/authorized_keys")

@parallel
def change_log(log):
    if not  exists("/root/.config/seed"):
        run("mkdir /root/.config/seed/ && echo 'INFO' >> /root/.config/seed/log_config")
    run("echo '{}' >> /root/.config/seed/log_config".format(log), quiet=True)
    run("cat /root/.config/seed/log_config")

def exchange_ssh_key(*servers):
    env.hosts += servers
    ssh = execute(ssh_key)
    authorized_keys = '\n'.join(list(ssh.values()) + [local_pub] ).encode('utf8')
    execute(upload_pub_key, authorized_keys)

@parallel
def shadowsocks_start(*args):
    if not run("pip3 list 2>/dev/null | grep shadowsocks | grep -v 'grep' | xargs", quiet=True):
        ex("pip3 install shadowsocks ")
    if not exists("/etc/shadowsocks.json"):
        ss_json = """{
    "server":"0.0.0.0",
    "port_password": {
        "13001": "thefoolish1",
        "13002": "thefoolish2",
        "13003": "thefoolish3",
        "13004": "thefoolish4",
        "13005": "thefoolish5",
        "13006": "thefoolish6",
        "13007": "thefoolish7",
        "13008": "thefoolish8",
        "13009": "thefoolish9",
        "13010": "thefoolish10",
        "13011": "thefoolish11",
        "13012": "thefoolish12",
        "13013": "thefoolish13"
    },
    "workers": 15,
    "method":"aes-256-cfb"
}"""
        with open("/tmp/sss.json", "w") as fp:fp.write(ss_json)
        put("/tmp/sss.json", "/etc/shadowsocks.json")
    if_start = run("ps aux | grep ssserver | grep json | grep -v 'grep' | awk '{print $2}' | xargs", quiet=True)
    if not if_start.strip():
        ex(PY3_ENV+ "ssserver -c /etc/shadowsocks.json -d start")
    else:
        ex(PY3_ENV +  "ssserver -c /etc/shadowsocks.json -d restart")
    if not exists("/tmp/pids"):
        ex("mkdir /tmp/pids",quiet=True)
    run("ps aux | grep ssserver | grep json | grep -v 'grep' | awk '{print $2}' | xargs > /tmp/pids/shadowsocks_server.pid", quiet=True)

def shadowsocks_pids():
    status = run("cat /tmp/pids/shadowsocks_server.pid")
    print(red(env.host), status)

def download(file):
    if exists(file):
        if not os.path.exists("/tmp/downloads"):
            os.mkdir("/tmp/downloads")
        filename = os.path.basename(file)
        get(file , "/tmp/downloads/" + filename)

def check_python_module(module):
    res = run("pip3 list 2>/dev/null | grep {m} | grep -v 'grep' | xargs".format(m=module),quiet=True)
    if res:
        return True
    return False

@parallel
def Update(file=None):
    if file and  os.path.exists(file):
        put(file, "/tmp/install.zip")
        if not exists("/tmp/install.zip"):
            print("upload failed", env.host)
        if check_python_module("x-mroy-1046"):
            run("pip3 uninstall -y x-mroy-1046 2>/dev/null", quiet=True)
            L("[rm] x-mroy-1046",env.host, color='green')
        r = run("pip3 install /tmp/install.zip 1>/dev/null 2>/dev/null  && echo 1", quiet=True)
        if r.strip() == '1':
            L("[update from local]", env.host, color='green')
        else:
            L("[failed update]" , env.host, color='green')
        return
    run(PY3_ENV + "pip3 uninstall -y x-mroy-1046", quiet=True)
    run(PY3_ENV + "pip3 install x-mroy-1046 --no-cache-dir ", quiet=True)
    r = run("pip3 list 2>/dev/null | grep x-mroy-1046 2>/dev/null",quiet=True)
    L('[ok]',r,env.host, color='green')
    #if exists("/tmp/seed.pip"):
     #   Startup("restart")
      #  L('[ok]', 'restart x-relay server', env.host, color='red')
    #else:
     #   Startup("start")

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
        yum -y install wget gcc make epel-release
        yum update -y
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
                 hash pip3 2>/dev/null;
                 if [ $? -eq  0 ];then

                     exit 0
                 else
                     apt install -y python3-pip python3-setuptools
                     exit 0
                 fi
        fi
    fi
fi

echo "command python can't be used.start installing python3.6."
cd /tmp
    if [ -f /tmp/Python-3.6.1.tgz ];then
      rm /tmp/Python-3.6.1.tgz;
    fi
wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
tar -zxvf Python-3.6.1.tgz
cd Python-3.6.1
mkdir /usr/local/python3
./configure --prefix=/usr/local/python3
make
make install
if [ -f /usr/bin/python3 ];then
   rm /usr/bin/python3;
   rm /usr/bin/pip3;
fi

if [ -f /usr/bin/lsb_release ];then
  rm /usr/bin/lsb_release;
fi

ln -s /usr/local/python3/bin/python3 /usr/bin/python3
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
echo 'export PATH="$PATH:/usr/local/python3/bin"' >> ~/.bashrc"""
    with open("/tmp/ini.sh", "w") as fp: fp.write(sh)
    put("/tmp/ini.sh", "/tmp/init.sh")
    run("bash /tmp/init.sh")
    print('[base]',env.host, " --- build [ok]")
    res = run("pip3 list 2>/dev/null | grep x-mroy-1046 | grep -v 'grep' |xargs", quiet=True)
    print("[Build]",env.host, res)
    if not res:
        run(PY3_ENV + "pip3 install x-mroy-1046 --no-cache-dir 1>/dev/null ")
    res = run("pip3 list 2>/dev/null | grep shadowsocks |grep -v 'grep' | xargs ", quiet=True)
    if not res:
        run("pip3 install shadowsocks --no-cache-dir ", quiet=True)
        print("[shadowsocks]", env.host, "  --- ok")
    if run("hash iptables-restore 1>/dev/null 2>/dev/null && echo 0", quiet=True):
        fi ="""
# Generated by iptables-save v1.4.21 on Sat Apr 28 10:24:41 2018
*nat
:PREROUTING ACCEPT [1:40]
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [1:76]
:POSTROUTING ACCEPT [1:76]
:OUTPUT_direct - [0:0]
:POSTROUTING_ZONES - [0:0]
:POSTROUTING_ZONES_SOURCE - [0:0]
:POSTROUTING_direct - [0:0]
:POST_public - [0:0]
:POST_public_allow - [0:0]
:POST_public_deny - [0:0]
:POST_public_log - [0:0]
:PREROUTING_ZONES - [0:0]
:PREROUTING_ZONES_SOURCE - [0:0]
:PREROUTING_direct - [0:0]
:PRE_public - [0:0]
:PRE_public_allow - [0:0]
:PRE_public_deny - [0:0]
:PRE_public_log - [0:0]
-A PREROUTING -j PREROUTING_direct
-A PREROUTING -j PREROUTING_ZONES_SOURCE
-A PREROUTING -j PREROUTING_ZONES
-A OUTPUT -j OUTPUT_direct
-A POSTROUTING -j POSTROUTING_direct
-A POSTROUTING -j POSTROUTING_ZONES_SOURCE
-A POSTROUTING -j POSTROUTING_ZONES
-A POSTROUTING_ZONES -o eth0 -g POST_public
-A POSTROUTING_ZONES -g POST_public
-A POST_public -j POST_public_log
-A POST_public -j POST_public_deny
-A POST_public -j POST_public_allow
-A PREROUTING_ZONES -i eth0 -g PRE_public
-A PREROUTING_ZONES -g PRE_public
-A PRE_public -j PRE_public_log
-A PRE_public -j PRE_public_deny
-A PRE_public -j PRE_public_allow
COMMIT
# Completed on Sat Apr 28 10:24:41 2018
# Generated by iptables-save v1.4.21 on Sat Apr 28 10:24:41 2018
*mangle
:PREROUTING ACCEPT [254:19298]
:INPUT ACCEPT [254:19298]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [151:15843]
:POSTROUTING ACCEPT [151:15843]
:FORWARD_direct - [0:0]
:INPUT_direct - [0:0]
:OUTPUT_direct - [0:0]
:POSTROUTING_direct - [0:0]
:PREROUTING_ZONES - [0:0]
:PREROUTING_ZONES_SOURCE - [0:0]
:PREROUTING_direct - [0:0]
:PRE_public - [0:0]
:PRE_public_allow - [0:0]
:PRE_public_deny - [0:0]
:PRE_public_log - [0:0]
-A PREROUTING -j PREROUTING_direct
-A PREROUTING -j PREROUTING_ZONES_SOURCE
-A PREROUTING -j PREROUTING_ZONES
-A INPUT -j INPUT_direct
-A FORWARD -j FORWARD_direct
-A OUTPUT -j OUTPUT_direct
-A POSTROUTING -j POSTROUTING_direct
-A PREROUTING_ZONES -i eth0 -g PRE_public
-A PREROUTING_ZONES -g PRE_public
-A PRE_public -j PRE_public_log
-A PRE_public -j PRE_public_deny
-A PRE_public -j PRE_public_allow
COMMIT
# Completed on Sat Apr 28 10:24:41 2018
# Generated by iptables-save v1.4.21 on Sat Apr 28 10:24:41 2018
*security
:INPUT ACCEPT [253:19258]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [151:15843]
:FORWARD_direct - [0:0]
:INPUT_direct - [0:0]
:OUTPUT_direct - [0:0]
-A INPUT -j INPUT_direct
-A FORWARD -j FORWARD_direct
-A OUTPUT -j OUTPUT_direct
COMMIT
# Completed on Sat Apr 28 10:24:41 2018
# Generated by iptables-save v1.4.21 on Sat Apr 28 10:24:41 2018
*raw
:PREROUTING ACCEPT [254:19298]
:OUTPUT ACCEPT [151:15843]
:OUTPUT_direct - [0:0]
:PREROUTING_ZONES - [0:0]
:PREROUTING_ZONES_SOURCE - [0:0]
:PREROUTING_direct - [0:0]
:PRE_public - [0:0]
:PRE_public_allow - [0:0]
:PRE_public_deny - [0:0]
:PRE_public_log - [0:0]
-A PREROUTING -j PREROUTING_direct
-A PREROUTING -j PREROUTING_ZONES_SOURCE
-A PREROUTING -j PREROUTING_ZONES
-A OUTPUT -j OUTPUT_direct
-A PREROUTING_ZONES -i eth0 -g PRE_public
-A PREROUTING_ZONES -g PRE_public
-A PRE_public -j PRE_public_log
-A PRE_public -j PRE_public_deny
-A PRE_public -j PRE_public_allow
COMMIT
# Completed on Sat Apr 28 10:24:41 2018
# Generated by iptables-save v1.4.21 on Sat Apr 28 10:24:41 2018
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [2310:506649]
:FORWARD_IN_ZONES - [0:0]
:FORWARD_IN_ZONES_SOURCE - [0:0]
:FORWARD_OUT_ZONES - [0:0]
:FORWARD_OUT_ZONES_SOURCE - [0:0]
:FORWARD_direct - [0:0]
:FWDI_public - [0:0]
:FWDI_public_allow - [0:0]
:FWDI_public_deny - [0:0]
:FWDI_public_log - [0:0]
:FWDO_public - [0:0]
:FWDO_public_allow - [0:0]
:FWDO_public_deny - [0:0]
:FWDO_public_log - [0:0]
:INPUT_ZONES - [0:0]
:INPUT_ZONES_SOURCE - [0:0]
:INPUT_direct - [0:0]
:IN_public - [0:0]
:IN_public_allow - [0:0]
:IN_public_deny - [0:0]
:IN_public_log - [0:0]
:OUTPUT_direct - [0:0]
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -j INPUT_direct
-A INPUT -j INPUT_ZONES_SOURCE
-A INPUT -j INPUT_ZONES
-A INPUT -m conntrack --ctstate INVALID -j DROP
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A FORWARD -i lo -j ACCEPT
-A FORWARD -j FORWARD_direct
-A FORWARD -j FORWARD_IN_ZONES_SOURCE
-A FORWARD -j FORWARD_IN_ZONES
-A FORWARD -j FORWARD_OUT_ZONES_SOURCE
-A FORWARD -j FORWARD_OUT_ZONES
-A FORWARD -m conntrack --ctstate INVALID -j DROP
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
-A OUTPUT -j OUTPUT_direct
-A FORWARD_IN_ZONES -i eth0 -g FWDI_public
-A FORWARD_IN_ZONES -g FWDI_public
-A FORWARD_OUT_ZONES -o eth0 -g FWDO_public
-A FORWARD_OUT_ZONES -g FWDO_public
-A FWDI_public -j FWDI_public_log
-A FWDI_public -j FWDI_public_deny
-A FWDI_public -j FWDI_public_allow
-A FWDI_public -p icmp -j ACCEPT
-A FWDO_public -j FWDO_public_log
-A FWDO_public -j FWDO_public_deny
-A FWDO_public -j FWDO_public_allow
-A INPUT_ZONES -i eth0 -g IN_public
-A INPUT_ZONES -g IN_public
-A IN_public -j IN_public_log
-A IN_public -j IN_public_deny
-A IN_public -j IN_public_allow
-A IN_public -p icmp -j ACCEPT
-A IN_public_allow -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT
-A IN_public_allow -p tcp -m tcp --dport 13001:13011 -j ACCEPT
-A IN_public_allow -p udp -m udp --dport 13001:13011 -j ACCEPT
-A IN_public_allow -p tcp -m tcp --dport 60000:61000 -j ACCEPT
-A IN_public_allow -p udp -m udp --dport 60000:61000 -j ACCEPT
COMMIT
# Completed on Sat Apr 28 10:24:41 2018
"""
        with open("/tmp/fi", "w") as fp: fp.write(fi)
        put("/tmp/fi", "/tmp/fi")
        run('hash iptables-restore && iptables-restore < /tmp/fi')

def Generate_Qr(dirs, host):
    if not os.path.exists(dirs): return
    code = 'ss://' + b64encode('aes-256-cfb:thefoolish2@{host}:13002'.format(host=host).encode('utf8')).decode('utf8')
    cmd = 'echo "' + code + '" | qr >  ' + dirs + '/' + host.strip() + ".png"
    print(cmd)
    os.popen(cmd)

@parallel
def Startup(arg):
    if arg=='start':
        run(PY3_ENV + 'x-relay start')
        run(PY3_ENV + 'x-bak start')

    elif arg == 'stop':
        run(PY3_ENV + 'x-relay stop')
        run(PY3_ENV + 'x-bak stop')
    elif arg == 'restart':
        run(PY3_ENV + 'x-relay stop && x-relay start')
        run(PY3_ENV + 'x-bak stop && x-bak start')

@parallel
def sync(target, files):
    if not exists(target):
        print("not found ", target, 'in serer')
        return
    for file in files:
        put(file, os.path.join(target, os.path.basename(file)))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a","--add-host", default=False, action='store_true', help='add a host to db')
    parser.add_argument("-s","--search", default=None, help="search local's db ")
    parser.add_argument("-d","--delete", default=False, action='store_true', help='if -s xxx -d will delete content')
    parser.add_argument("-I","--init-env", default=False, action='store_true', help='if true, will exchange_ssh_key and check then build some base env')
    parser.add_argument("-e","--execute", nargs="*", default=None, help="run some command in server")
    parser.add_argument("-S","--startup", default=None, help="start | restart | stop")
    parser.add_argument("-U", "--update", default=False, action='store_true', help='update x-mroy-1046 remote work with -s xxx or update all')
    parser.add_argument("--shadowsocks", default=False, action='store_true', help='if set, will deploy shadowsocks')
    parser.add_argument("--export-qr", default=None, type=str, help='export servers to qr img ')
    parser.add_argument("-D", "--download", default=None, type=str, help="download from remote server")
    parser.add_argument("--sync", nargs="+", default=None,help="sync file to remote server : --sync local_file1 local_file2 remote_dir")
    parser.add_argument("--ifup", default=False, action='store_true', help=" check if all hosts up")
    parser.add_argument("-P", "--path", default=None, help="set file path, use for other option like : -U ")
    parser.add_argument("--sync-ssh", default=False, action='store_true',help="if true will sync ssh_pub_key . you can use -s to select part of hosts")
    parser.add_argument("--log", default=None, help=" [info / error / debug / warrn] ")
    args = parser.parse_args()

    if args.log:
        if not os.path.exists(os.getenv("HOME") + "/.config/seed"):
            os.mkdir(os.getenv("HOME") + "/.config/seed")
        with open(os.getenv("HOME") + "/.config/seed/log_config", "w") as fp:
            fp.write(args.log.upper())

    if args.add_host:
        host = prompt("host=",default=None)
        if not host:
            print("must be a valid host")
            sys.exit(0)
        port = prompt("port=",default="22")
        user = prompt("user=",default="root")
        add_host(host,port=port,user=user)

        sys.exit(0)

    if args.ifup:
        tester = Test()
        tester.check_hosts()

    if args.search:
        hs = []
        for host in hosts_db.query(Host):
            if args.search in host.host:
                host.display()
                hs.append(host)
        if args.execute:
            [h.patch() for h in hs]
            execute(exd, ' '.join(args.execute))
            sys.exit(0)

        if args.sync and len(args.sync) > 1:
            [h.patch() for h in hs]
            target = args.sync.pop()
            files = args.sync
            execute(sync , target, files)
            sys.exit(0)

        if args.download:
            [h.patch() for h in hs]
            execute(download, args.download)
            sys.exit(0)

        if args.delete:
            for h in hs:
                hosts_db.delete(h)
        elif args.startup:
            for h in hs:
                h.patch()
            execute(Startup, args.startup)
        elif args.update:
            [h.patch() for h in hs]
            if args.path and os.path.exists(args.path):
                print("Deal local file : ", args.path)
                with zipfile.ZipFile("/tmp/install.zip", "w") as zip:
                    for root, dirs, files in os.walk(args.path):
                        for file in files:
                            f = os.path.join(root, file)
                            zip.write(f)
                print("[pre deal] ")
            execute(Update, file="/tmp/install.zip")
            execute(Startup, "restart")
        elif args.shadowsocks:
            for h in hs:
                h.patch()
            execute(shadowsocks_start)
            execute(shadowsocks_pids)
        elif args.sync_ssh:
            [h.patch() for h in hs]
            exchange_ssh_key()
            sys.exit(0)

        elif args.init_env:
            [h.patch() for h in hs]
            execute(initenv)
            exchange_ssh_key()
            sys.exit(0)
        elif args.log:
            [h.patch() for h in hs]
            execute(change_log, args.log)
        sys.exit(0)
    if args.update:
        [h.patch() for h in hosts_db.query(Host)]
        if args.path and os.path.exists(args.path):
            print("Deal local file : ", args.path)
            with zipfile.ZipFile("/tmp/install.zip", "w") as zip:
                for root, dirs, files in os.walk(args.path):
                    for file in files:
                        f = os.path.join(root, file)
                        zip.write(f)
            print("[pre deal] ")
        execute(Update, file="/tmp/install.zip")
        sys.exit(0)

    if args.export_qr:
        ips = [h.host for h in hosts_db.query(Host)]
        for ip in ips:
            Generate_Qr(args.export_qr, ip)

    if args.sync_ssh:
        [h.patch() for h in hosts_db.query(Host)]
        exchange_ssh_key()
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

    if args.shadowsocks:
        [h.patch() for h in hosts_db.query(Host)]
        execute(shadowsocks)

    if args.execute:
        [h.patch() for h in hosts_db.query(Host)]
        execute(ex, ' '.join(args.execute))
