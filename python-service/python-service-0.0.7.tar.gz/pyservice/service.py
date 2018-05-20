#https://stackoverflow.com/a/8375012
import daemon
import argparse
import sys
import socket
import json
from daemon.pidfile import PIDLockFile
import lockfile
import traceback
import select
import time
import glob
import re
import os
import setproctitle

import time

#should use lockfile in /var/run but using ~ for now to avoid sudo
LOCKFILE_DIR = os.path.expanduser("~")

def send_args():
    return sys.argv

def empty_fn():
    pass

def print_fn(x):
    print(x)

class Service():
    #tutorial for python daemon
    #https://dpbl.wordpress.com/2017/02/12/a-tutorial-on-python-daemon/
    def __init__(self, name, daemon_setup=empty_fn, daemon_main=empty_fn, client_sender=send_args, client_receiver=print_fn):
        self.name = name
        self.daemon_setup = daemon_setup #no args
        self.daemon_main = daemon_main #array of sys.argv -> string
        self.client_sender = client_sender #() -> string
        self.client_receiver = client_receiver #string -> ()
    def get_desired_port(self):
        existing_lockfiles = glob.glob(LOCKFILE_DIR+'/.service_*.pid')
        this_service_lockfiles = [re.findall(LOCKFILE_DIR+'/\.service_(\d+)_'+self.name+'.pid',g) for g in existing_lockfiles]
        this_service_ports = [g[0] for g in this_service_lockfiles if g]
        all_service_ports = [int(re.findall(LOCKFILE_DIR+'/\.service_(\d+)_',g)[0]) for g in existing_lockfiles]
        if len(this_service_ports) > 1:
            raise Exception("Multiple existing lockfiles for service {self.name}".format(**vars()))
        elif len(this_service_ports) == 1:
            return this_service_ports[0]
        elif all_service_ports:
            return max(all_service_ports) + 1
        else:
            return 8047
    def get_daemon_port(self):
        existing_lockfiles = glob.glob(LOCKFILE_DIR+'/.service_*.pid')
        this_service_lockfiles = [re.findall(LOCKFILE_DIR+'/\.service_(\d+)_'+self.name+'.pid',g) for g in existing_lockfiles]
        this_service_ports = [int(g[0]) for g in this_service_lockfiles if g]
        if len(this_service_ports) > 1:
            raise Exception("Multiple ports for this service {self.name}".format(**vars()))
        elif len(this_service_ports) == 0:
            raise Exception("No daemon running")
        else:
            return this_service_ports[0]
    def run(self):

        #for fun: explanations of unix double fork
        #https://stackoverflow.com/a/45912948
        #https://stackoverflow.com/a/5386753
        #However: double fork handled by python daemon module
        #so we can just fork once

        #fork and start the daemon if not already running
        newpid = os.fork()
        if newpid == 0: #child starts the daemon
            setproctitle.setproctitle(sys.argv[0] + " --daemon")
            port = self.get_desired_port()
            while True:
                try:
                    self.run_daemon(port)
                    break
                except OSError as e:
                    port = port + 1
                    print('port in use...')
        else: #parent runs the client
            self.run_client()
    def run_daemon(self, port):
        #checking lockfile outside of daemoncontext because daemoncontext does strange things to the process even if an exception breaks us out of it
        lockfile = PIDLockFile(LOCKFILE_DIR + '/.service_{port}_{self.name}.pid'.format(**vars()))
        if lockfile.is_locked():
            return

        print('running daemon from port {port}'.format(**vars()))
        time.sleep(0.1)
        with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, pidfile=lockfile):
            self.daemon_setup()

            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.bind(('localhost', port))
            serversocket.listen(5) # become a server socket, maximum 5 connections

            sys.stdout.flush()
            #TODO: remove this try/except (daemon_loop try/except should suffice)
            self.daemon_loop(serversocket)

            serversocket.close()
    def daemon_loop(self, serversocket):
        sys.stdout.flush()
        while True:
            sys.stdout.flush()
            time.sleep(1)
            connection, address = serversocket.accept()
            input_ = json.loads(read_connection(connection))
            try:
                out = {"out":self.daemon_main(input_)}
            except:
                out = {"err":traceback.format_exc()}

            connection.send(json.dumps(out).encode('utf-8'))
            connection.close()
    def run_client(self):
        retry_cnt = 0
        while True:
            try:
                port = self.get_daemon_port()
                break
            except:
                if retry_cnt >= 3:
                    raise
                else:
                    #wait for the daemon to start up
                    time.sleep(1)
                    retry_cnt = retry_cnt + 1

        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect(('localhost', port))
        clientsocket.send(json.dumps(self.client_sender()).encode('utf-8'))
        output = json.loads(read_connection(clientsocket))

        if "err" in output:
            sys.stderr.write(output["err"])
        else:
            self.client_receiver(output["out"])

def read_connection(connection):
    out = b""
    while True:
        #https://stackoverflow.com/a/2721734
        TIMEOUT = 0.01 #is it ok to use a timeout this low?
        ready = select.select([connection], [], [], TIMEOUT)
        if ready[0]:
            buf = connection.recv(4)
            if len(buf) > 0:
                out += buf
            else:
                #why do we get here sometimes even though ready[0] = true?
                #breaking for now (ie assume no more data is coming)
                break
        else:
            #if we have some data break out and return it, otherwise
            #keep spinning / waiting for data
            if out:
                break
    return out

# if __name__ == "__main__":
#     Service(daemon_main=body).run()
