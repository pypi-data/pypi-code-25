import json
import sys
import socket
import threading
import time
from select import select

import sys
is_py2 = sys.version[0] == '2'

def main():
    msg_socket = socket.socket()
    args = sys.argv
    msg_socket.connect(('127.0.0.1', int(args[1])))
    run_event = threading.Event()

    receiving = threading.Thread(target = in_thread, args = (msg_socket, run_event))
    sending = threading.Thread(target = out_thread, args = (msg_socket, run_event))

    receiving.start()
    sending.start()

    print("threads started")

def in_thread(msg_socket, run_event):
    while (not run_event.is_set()):
        in_message = msg_socket.recv(1024).decode('utf-8')
        if in_message is not None:
            print(in_message)
            print(len(in_message))
        if len(in_message) == 0:
            end_processes(msg_socket, run_event)
        time.sleep(0.5)
    print("in_thread closed")

def out_thread(msg_socket, run_event):
    while (not run_event.is_set()):
        timeout = 10
        try:
            rlist, _, _ = select([sys.stdin], [], [], timeout)
            if rlist:
                message = sys.stdin.readline()
                if len(message) > 0 and message is not None:
                    data = {'message': message, 'message_id': 1}
                    print("sending " + message)
                    msg_socket.send(json.dumps(data).encode('utf-8'))
            else:
                continue
        except KeyboardInterrupt:
            end_processes(msg_socket, run_event)
            return True
    print("out_thread closed")

def end_processes(msg_socket, run_event):
    print("shutting down..")
    run_event.set()
    msg_socket.shutdown(socket.SHUT_RDWR)
    print("socket shutted down")
    return []
