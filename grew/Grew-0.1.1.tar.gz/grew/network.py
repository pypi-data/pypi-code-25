''' Utility tools to connect to ocaml GREW'''

import subprocess
import time
import socket
import os.path
import json
import utils
import grew

host = 'localhost'
port = 8888
remote_ip = ''

def init():
    global port, remote_ip
    python_pid = os.getpid()
    while (port<8898):
        caml = subprocess.Popen(["grewpy_daemon", "--caller", str(python_pid), "--port", str(port)])
        #wait for grew's lib answer
        time.sleep(0.1)
        if caml.poll() == None:
            print ("connected to port: " + str(port))
            remote_ip = socket.gethostbyname(host)
            return (caml)
        else:
            port += 1
    print ("Failed to connect 10 times!")
    exit (1)

def connect():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((remote_ip, port))
        return s
    except socket.error:
        print('[GREW] Failed to create socket. Sorry\n')
    except socket.gaierror:
        print('[GREW] Hostname could not be resolved. Sorry\n')


def send_and_receive(msg):
    try:
        stocaml = connect()
        json_msg = json.dumps(msg)
        stocaml.sendall(json_msg.encode(encoding='UTF-8'))
        camltos = stocaml.recv(4096)
        stocaml.close()
        reply = json.loads(camltos.decode(encoding='UTF-8'))
        if reply["status"] == "OK":
            return reply["data"]
        elif reply["status"] == "ERROR":
            raise utils.GrewError (reply["message"])
    except socket.error:
        raise grew.GrewError('Library call socket error')
    except AttributeError: # connect issue
        raise grew.GrewError('Library call AttributeError')

