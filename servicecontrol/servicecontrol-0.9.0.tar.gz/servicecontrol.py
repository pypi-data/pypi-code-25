# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 08:18:59 2017

This script is designed to wrap around external services
and provide access to starting/stopping that service
using remote procedure calls.

The reason is to allow adfags to start/stop spacelink and potentially
also gnuradio and hamlib when it needs to and thereby improve reliability


@author: kjetil
"""
from __future__ import print_function


from SimpleXMLRPCServer import SimpleXMLRPCServer
#from xmlrpclib import ServerProxy
import subprocess
import threading
import argparse
import select
import os
import sys
import logging
import logging.handlers
import signal
import time

class LogFormatter(logging.Formatter):
    converter = time.gmtime

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        t = time.strftime("%Y-%m-%dT%H:%M:%S", ct)
        s = "%s.%03dZ" % (t, record.msecs)

        return s

log = logging.getLogger('servicecontrol')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
formatter = LogFormatter('%(asctime)s - %(levelname)5s - "%(message)s"')
ch.setFormatter(formatter)
log.addHandler(ch)


class ServiceControl():

    # Maximum number of lines of stdout/stderr to keep in memory
    # to be returned on request over RPC
    MAX_BUFLEN = 50

    #
    # Number of seconds to allow for boot errors before initiating auto-restart sequences
    #
    MIN_BOOT_TIME = 3.0

    def __init__(self, args, addr="localhost", port=9000, echo=True, autorestart=False, cputhreshold = None):
        self.args = args
        self._p = None
        self._addr = addr
        self._port = port
        self._stdout = []
        self._stderr = []
        self.cpu_threshold = cputhreshold
        #self._buf = dict()
        self._echo = echo
        self._stop_monitor = False

        self.autorestart = autorestart

        self.server = SimpleXMLRPCServer((self._addr, self._port), allow_none=True)
        self._pthr_rpc = threading.Thread(target=self.server.serve_forever)
        self._pthr_rpc.daemon = True
        self._pthr_rpc.start()

        # Make RPC calls more usable by publishing functions
        self.server.register_introspection_functions()

        # Register the functions
        self.server.register_function(self.start)
        self.server.register_function(self.kill)
        self.server.register_function(self.stdout)
        self.server.register_function(self.stderr)
        self.server.register_function(self.pid)
        self.server.register_function(self.pgid)
        self.server.register_function(self.cpu)



    def _monitor_cpu(self):

        count = 0
        COUNT_THRESHOLD = 3
        POLLING_INTERVAL = 1.0
        self._stop_monitor = False


        if self.cpu_threshold is None:
            log.error("CPU threshold not set, cant monitor cpu")


        while (True):

            if self._stop_monitor:
                break

            c = self.cpu()

            if c > self.cpu_threshold:
                if count >= COUNT_THRESHOLD:
                    log.info("Restarting service. Reason: continued excess CPU usage")
                    sys.stdout.flush()
                    break

                count += 1
                log.info("Excess CPU usage (%.1f%%) detected. Allowing %d/%d"%(c, count, COUNT_THRESHOLD))
                sys.stdout.flush()



            time.sleep(POLLING_INTERVAL)

        if not self._stop_monitor:
            self.kill()
            time.sleep(1)
            self.start()


    def _get_pipes(self):
        poller = select.poll()
        poller.register(self._p.stdout, select.POLLIN)
        poller.register(self._p.stderr, select.POLLIN)

        scmap = {\
            self._p.stdout.fileno():(self._p.stdout, self._stdout, sys.stdout),
            self._p.stderr.fileno():(self._p.stderr, self._stderr, sys.stderr)}

        t0 = time.time()

        while self._p.poll() is None:

            polled = poller.poll(100)
            #print('AA %s'%(polled))
            streams = [scmap[p[0]] for p in polled]

            for stream in streams:
                so = stream[0].readline()[:-1]
                #so = os.read(polled[0][0], 1)#read(1)
                if so:
                    if self._echo:
                        #print("%s"%so, file=stream[2], end='')
                        #stream[2].flush()
                        log.debug("%s"%so)

                    #stream[1].append(so)
                    self._stdout =  self._stdout[-self.MAX_BUFLEN:]
                    self._stderr =  self._stderr[-self.MAX_BUFLEN:]

        log.info("Process stopped")

        if self._echo:
            log.debug("%s"%self._p.stdout.read())
            log.debug("%s"%self._p.stderr.read())

        #print(sc._p.stdout.read())
        #print(sc._p.stderr.read(), file=sys.stderr)
        self._p = None


        # Check if program died a natural death, and if not restart
        # if the autorestart flag has been set.
        # and only do so if some time has passed (in order to prevent constant
        # restart loops)
        if self._should_still_be_running and self.autorestart and time.time() - t0 > self.MIN_BOOT_TIME:
            self.start()


    def start(self):
        if self._p is not None:
            log.error('Process already running')
            return

        self._p = subprocess.Popen(
            self.args,
            bufsize=1,
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
            cwd=None,
            universal_newlines=True,
            )


        self._pthr = threading.Thread(target=self._get_pipes)
        self._pthr.daemon = True
        self._pthr.start()


        if self.cpu_threshold is not None:
            self._pthr_cpumon = threading.Thread(target=self._monitor_cpu)
            self._pthr_cpumon.daemon = True
            self._pthr_cpumon.start()


        self._should_still_be_running = True


    def _ps(self, option):
        ret = subprocess.check_output(["ps", "-p", "%s"%(self.pid()), "-o", option,"--no-headers"])
        return ret.strip()


    def cpu(self):
        return float(self._ps("pcpu"))
#        #TODO: Check if I should check PID or PGID
#        #TODO: Find a way to set custom delimiter. Limiting by field width is not nice
#        FW = 100
#        ps_fields = ['pcpu','pid','pgid','sid','user','args']
#        ps_fields2 = ["%s:%d"%(p,FW) for p in ps_fields]
#        ret = subprocess.check_output(["ps", "-p", "%s"%(self.pid()), "-o", ",".join(ps_fields2),"--no-headers"])
#
#        retd = {}
#        for k,v in enumerate(ps_fields):
#            retd[v] = ret[k*FW:(k+1)*FW].strip()
#
#        return retd

    def pid(self):
        return self._p.pid

    def pgid(self):
        return os.getpgid(self._p.pid)

    def kill(self, sig=signal.SIGTERM):
        if self._p is None:
            log.error('Process is not running')
            return
        else:
            self._stop_monitor = True
            os.killpg(os.getpgid(self._p.pid), signal.SIGTERM)
            self._should_still_be_running = False
            self._pthr.join()
            self._p = None


    def stdout(self):
        if self._p is None:
            log.error('Process is not running')
            return ''
        else:
            return ''.join(self._stdout)


    def stderr(self):
        if self._p is None:
            log.error('Process is not running')
            return ''
        else:
            return ''.join(self._stderr)






def main():
    
    try:
        select.poll
    except:
        print("servicecontrol requires select.poll which is not available", file=sys.stderr)
        print("on your current OS + Python combination.", file=sys.stderr)
        print("Note that on Macos select.poll is not available by default,", file=sys.stderr)
        print("but *is* available in some distributions such as anaconda", file=sys.stderr)
        exit(1)

    #
    # Parse command line
    #
    parser = argparse.ArgumentParser()

    parser.add_argument("--start", action="store_true")
    parser.add_argument("--addr", type=str, default="localhost", help="xmlrpc address, default=localhost")
    parser.add_argument("--port", type=int, default= 9001, help = "xmlrpc port, default=9001")
    parser.add_argument("--no-echo", action="store_true")
    parser.add_argument("--autorestart", action="store_true")
    parser.add_argument("--cpurestart", type=float, help="Set CPU threshold to automatically restart service at")
    parser.add_argument("--log", type=str, help="Filename to log to (default is None - stdout only)" )
    parser.add_argument("-i", "--interact", action="store_true")
    parser.add_argument("cmd", help="The command to parse")

    args = parser.parse_args()

    # actual command to run
    import shlex
    argv = shlex.split(args.cmd)

    # Enable logging
    if args.log is not None:
        cf = logging.handlers.TimedRotatingFileHandler(args.log,when='midnight',interval=1,backupCount=0,utc=True)
        #cf = logging.FileHandler(args.log)
        formatter = LogFormatter('%(asctime)s - %(levelname)5s - "%(message)s"')
        cf.setFormatter(formatter)
        log.addHandler(cf)


    sc = ServiceControl(argv, addr=args.addr, port=args.port,echo=(not args.no_echo), autorestart=args.autorestart, cputhreshold = args.cpurestart)

    if args.start is True:
        sc.start()

    if args.interact:
        #
        # Define some wrapper functions to save user having to type sc.xxx
        #
        def kill(sig=signal.SIGTERM):
            sc.kill(sig)

        def start():
            sc.start()

        def pid():
            return sc.pid()

        def pgid():
            return sc.pgid()

        def cpu():
            return sc.cpu()

        import code
        code.interact(local=locals())
    else:
        #Non-interactive mode. Loop forever
        #Todo: catch/handle signals?
        while True:
            time.sleep(1)

    sc.kill()


if __name__ == '__main__':
    main()