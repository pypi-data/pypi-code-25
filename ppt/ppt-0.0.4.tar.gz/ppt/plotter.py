#!/usr/bin/env python3

import numpy as np
import os
import sys
import subprocess
import logging
import time
import signal
import visdom
import logging
from multiprocessing import Process
from visdom.server import download_scripts, main, start_server


def kill_child_processes(signum, frame):
    parent_id = os.getpid()
    ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_id, shell=True, stdout=subprocess.PIPE)
    ps_output = ps_command.stdout.read()
    retcode = ps_command.wait()
    for pid_str in ps_output.strip().split("\n")[:-1]:
        os.kill(int(pid_str), signal.SIGTERM)
    sys.exit()


class Plotter(object):

    def __init__(self, env='main'):
        self.sessions = None
        self.visdom_server = None
        self.data = None
        self.env = env

    def _start_visdom_server(self):
        def server():
            sys.stdout = open(os.devnull, "w")
            logging.getLogger().setLevel(logging.ERROR)
            start_server()
        download_scripts()
        self.visdom_server = Process(target=server)
        self.visdom_server.start()
        signal.signal(signal.SIGTERM, kill_child_processes)
        time.sleep(1.0)
        print('Visdom was started on localhost:8097.')


    def _init_sessions(self):
        vis = visdom.Visdom(env=self.env)
        self.visdom = vis
        self.sessions = {}
        self.data = {}
        

    def plot(self, value=0.0, name=None):
        # Updates live visualizations for all metrics
        if self.sessions is None:
            self._init_sessions()

        if not self.visdom.check_connection():
            self._start_visdom_server()

        if name is None:
            name = 'ppt_default'
        if name not in self.sessions:
            self.sessions[name] = self.visdom.line(X=np.zeros(1),
                                                   Y=np.zeros(1),
                                                   opts={'title': name})
            self.data[name] = []


        self.data[name].append(value)
        self.visdom.line(X=np.arange(len(self.data[name])),
                         Y=np.array(self.data[name]),
                         win=self.sessions[name],
                         update='replace')

    def close(self):
        if self.visdom_server is not None:
            self.visdom_server.terminate()
