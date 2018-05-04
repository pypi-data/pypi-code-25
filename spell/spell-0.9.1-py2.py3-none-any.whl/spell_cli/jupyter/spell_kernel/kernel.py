#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import copy
import json
import logging
import queue
import signal
import sys
import threading

from IPython.core.ultratb import AutoFormattedTB
from jupyter_client.session import Session
import zmq
from zmq.eventloop import ioloop, zmqstream

from api_client import runs_client
from api_client.exceptions import UnauthorizedRequest, ClientException
from spell_cli.configs.config_handler import ConfigHandler
from spell_cli.exceptions import ConfigException
from spell_cli.utils import default_spell_dir, parse_utils
from spell_cli.utils.parse_utils import ParseException
from spell_cli.jupyter.spell_kernel.logger import SpellKernelLogger
from spell_cli.jupyter.spell_kernel.sshkernel import SSHKernel, SSHKernelException


KERNEL_PROTOCOL_VERSION = "5.1"
SPELL_KERNEL_VERSION = "0.1.0"


class SpellKernelException(Exception):
    pass


class SpellKernel(object):
    _kernel_info = {
        "protocol_version": KERNEL_PROTOCOL_VERSION,
        "implementation": "spell_kernel",
        "implementation_version": SPELL_KERNEL_VERSION,
        "banner": "Spell kernel (v{})".format(SPELL_KERNEL_VERSION),
        "language_info": {
            "mimetype": "text/x-python",
            "nbconvert_exporter": "python",
            "name": "python",
            # TODO(peter): Make Python version configurable
            "pygments_lexer": "ipython2",
            "version": "3.6.4",
            "file_extension": ".py",
            "codemirror_mode": "python"
        },
        # TODO(peter): Include help_links to Spell docs
    }

    def __init__(self, machine_type, ssh_host, ssh_port, api_opts, run_opts, kernel_spec, username, keys=None):
        self.machine_type = machine_type
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.api_opts = api_opts
        self.run_opts = run_opts
        self.kernel_spec = kernel_spec
        self.username = username
        self.keys = [] if keys is None else keys

        self.logger = SpellKernelLogger("SpellKernel", level=logging.INFO)
        self.serializer = Session(
            username=self.username,
            signature_scheme=self.kernel_spec["signature_scheme"],
            key=self.kernel_spec.get("key", "").encode("utf-8"),
        )
        self.ioloop = ioloop.IOLoop.instance()
        self.run_id = None
        self.run_status_queue = queue.Queue()
        self.ssh_kernel = None
        self.color_tb = AutoFormattedTB(mode="Plain", color_scheme='LightBG')

        self._running = True
        self._sent_start_message = False
        self._waiting_cell = None
        self._exception = None

        self._message_lock = threading.Lock()
        self._messages = []
        self._message_queue = queue.Queue()

    def initial_setup(self):
        # Spin off thread for de-queueing log messages
        dequeue_log_thread = threading.Thread(target=self._dequeue_logs)
        dequeue_log_thread.start()

        # Spin off thread for starting run
        self.logger.info("Starting run")
        run_start_thread = threading.Thread(target=self.start_run)
        run_start_thread.start()

        # Set up the local sockets we need to do the initial handshake
        zmq_ctx = zmq.Context()
        self.local_streams = self._init_local_sockets(zmq_ctx)

        # Register callback for the initial kernel_info handshake
        self.local_streams["shell"].on_recv(self.handle_startup_shell)
        self.local_streams["control"].on_recv(self.handle_startup_control)
        self._log_to_cells("Preparing kernel, please wait...")

        # Handle interrupts
        signal.signal(signal.SIGINT, self.handle_startup_signals)

        # Start listening
        ioloop_thread = threading.Thread(target=self.ioloop.start)
        ioloop_thread.start()

        # Set up the sockets we'll need for the SSH kernel
        self.dummy_sockets, self.remote_ports = self._init_dummy_sockets(zmq_ctx)
        self.recv_streams = self._init_recv_sockets(zmq_ctx)

        # Wait for the run start thread to finish
        run_start_thread.join()

        # Start tracking the run status
        run_status_thread = threading.Thread(target=self.track_run_status)
        run_status_thread.start()

        # Build the SSH kernel
        self.logger.info("Building SSH kernel")
        ssh_config = self._build_ssh_config()
        connection_info = self._build_ssh_connection_info()
        self.ssh_kernel = SSHKernel(
            host=self.ssh_host,
            ssh_config=ssh_config,
            connection_info=connection_info,
            conda_env=self.run_opts["conda_env"],
        )

    def ssh_setup(self):
        # Start the kernel on the remote
        self.logger.info("Run is ready")
        self.logger.info("Initializing remote")
        self.logger.info("Establishing SSH connection")
        self._log_to_cells("Establishing connection to remote")
        try:
            self.ssh_kernel.connect_ssh()
        except SSHKernelException as e:
            exc_info = (
                SpellKernelException,
                SpellKernelException(str(e)),
                None,
            )
            self.handle_startup_exception(exc_info)
            return
        except Exception:
            self.handle_startup_exception(sys.exc_info())
            return

        self._log_to_cells("Starting kernel on remote")
        try:
            self.ssh_kernel.initialize_remote()
        except SSHKernelException as e:
            exc_info = (
                SpellKernelException,
                SpellKernelException(str(e)),
                None,
            )
            self.handle_startup_exception(exc_info)
            return
        except Exception:
            self.handle_startup_exception(sys.exc_info())
            return

        # Close the sockets that were reserving ports
        for socket in self.dummy_sockets.values():
            socket.close()
        # Set up the tunnels
        self._log_to_cells("Tunnelling ports")
        try:
            self.ssh_kernel.tunnel_ports()
        except SSHKernelException as e:
            exc_info = (
                SpellKernelException,
                SpellKernelException(str(e)),
                None,
            )
            self.handle_startup_exception(exc_info)
            return
        except Exception:
            self.handle_startup_exception(sys.exc_info())
            return

        # Stop the callbacks that were used for initialization
        self.local_streams["shell"].stop_on_recv()
        # Stitch the sockets receiving from client to those sending to remote
        self._log_to_cells("Finalizing connections to remote")
        self.stitch_sockets(self.local_streams, self.recv_streams)

        # Set kernel status to ready
        self._log_to_cells("Ready! Rerun command to run on {} machine".format(self.machine_type))
        if self._waiting_cell is not None:
            # Wait for queue to empty
            self._message_queue.join()

            with self._message_lock:
                content = {
                    "status": "ok",
                    "execution_count": 1,
                }
                self._send("shell", "execute_reply", content,
                           parent=self._waiting_cell["parent"],
                           ident=self._waiting_cell["ident"])
            self._waiting_cell = None

        content = {
            "execution_state": "idle",
        }
        self._send("iopub", "status", content)

        # Keep the kernel alive
        self.logger.info("Keeping kernel alive")
        signal.signal(signal.SIGINT, self.handle_signals)
        try:
            self.ssh_kernel.keep_alive()
        except Exception as e:
            self.logger.critical("Kernel has died: {}", e)

    def handle_startup_shell(self, msg_list):
        idents, msg = self._deserialize(msg_list)
        msg_type = msg["header"]["msg_type"]

        if msg_type == "kernel_info_request":
            if not self._sent_start_message:
                state = "starting"
                self._sent_start_message = True
            else:
                state = "idle"

            content = {
                "execution_state": state,
            }
            self._send("iopub", "status", content, parent=msg, ident=idents)
            self._send("shell", "kernel_info_reply", self._kernel_info, parent=msg, ident=idents)

        elif msg_type == "execute_request":
            # TODO(peter): Publish execute_input messages on iopub too
            self._waiting_cell = {"ident": idents, "parent": msg}
            if self._exception is not None:
                self.handle_startup_exception(self._exception)
            else:
                with self._message_lock:
                    for content in self._messages:
                        self._send("iopub", "stream", content,
                                   parent=self._waiting_cell["parent"],
                                   ident=self._waiting_cell["ident"],
                                   flush=True)

        elif msg_type == "shutdown_request":
            self.handle_shutdown(idents, msg)

    def handle_startup_control(self, msg_list):
        idents, msg = self._deserialize(msg_list)
        msg_type = msg["header"]["msg_type"]

        if msg_type == "shutdown_request":
            self.handle_shutdown(idents, msg)

    def handle_startup_signals(self, signum, frame):
        if signum == 2:
            self.logger.info("Interrupted")
            if self._waiting_cell is not None:
                content = {
                    "status": "error",
                }
                self._send("shell", "execute_reply", content,
                           parent=self._waiting_cell["parent"],
                           ident=self._waiting_cell["ident"])
                self._waiting_cell = None

    def handle_startup_exception(self, exc_info):
        self.logger.info("Exception raised")
        self._exception = exc_info
        self._running = False
        if self._waiting_cell is not None:
            etype, evalue, tb = exc_info

            evalue = SpellKernelException(str(evalue).strip())
            etype = type(evalue)
            if tb is not None:
                # Pretty-print stack traces if they exist
                self.color_tb.set_mode("Context")
                tb = self.color_tb.structured_traceback(etype, evalue, tb)
            else:
                tb = [line.strip() for line in self.color_tb.structured_traceback(etype, evalue, tb)]

            content = {
                "traceback": tb,
                "ename": etype.__name__,
                "evalue": str(evalue),
            }
            self._send("iopub", "error", content,
                       parent=self._waiting_cell["parent"],
                       ident=self._waiting_cell["ident"],
                       flush=True)
            content["status"] = "error"
            self._send("shell", "execute_reply", content,
                       parent=self._waiting_cell["parent"],
                       ident=self._waiting_cell["ident"])

            self._waiting_cell = None

    def handle_shutdown(self, idents, msg):
        stopped = False
        # Try stopping the run
        try:
            self.stop_run()
            stopped = True
        except ClientException as e:
            self.logger.warn("Failed to stop run: " + str(e))
        except Exception as e:
            self.logger.exception(str(e))

        # Kill the run
        try:
            if not stopped:
                self.kill_run()
        except ClientException as e:
            self.logger.warn("Failed to kill run: " + str(e))
        except Exception as e:
            self.logger.exception(str(e))

        # Stop the SSH kernel
        if self.ssh_kernel is not None:
            self.ssh_kernel._running = False

        # Stop the tornado ioloop
        self.ioloop.stop()

        # Reply to the restart request
        content = {
            "restart": msg["content"]["restart"],
        }
        self._send("shell", "shutdown_reply", content, parent=msg, ident=idents)

    def handle_signals(self, signum, frame):
        if signum == 2:
            self.logger.info("Interrupting remote kernel")
            self.ssh_kernel.interrupt()

    def stop_run(self):
        if self.run_id is None:
            return

        r_client = runs_client.RunsClient(**self.api_opts)
        r_client.stop_run(str(self.run_id))
        self.logger.info("Stopped run #{}".format(self.run_id))

    def kill_run(self):
        if self.run_id is None:
            return

        r_client = runs_client.RunsClient(**self.api_opts)
        r_client.kill_run(str(self.run_id))
        self.logger.info("Killed run #{}".format(self.run_id))

    def stitch_sockets(self, local_streams, recv_streams):
        for name in local_streams.keys():
            local_stream = local_streams[name]
            recv_stream = recv_streams[name]

            local_stream.on_recv(self.stitch_to(recv_stream, name, "local"))
            recv_stream.on_recv(self.stitch_to(local_stream, name, "recv"))

    def stitch_to(self, dest, name, src):
        if name == "iopub" or name == "stdin":
            def send_msg(raw_msg):
                dest.send_multipart(raw_msg)
        elif name == "shell" or name == "control":
            def send_msg(raw_msg):
                idents, msg = self._deserialize(raw_msg)
                if msg["header"]["msg_type"] == "shutdown_request":
                    self.handle_shutdown(idents, msg)
                dest.send_multipart(raw_msg)
        elif name == "hb":
            def send_msg(raw_msg):
                self.logger.info("Handling heartbeat message from {}".format(src))
                # TODO(peter): Implement this
                self.handle_hb(raw_msg)
        return send_msg

    def start_run(self):
        r_client = runs_client.RunsClient(**self.api_opts)
        try:
            attached_resources = parse_utils.parse_attached_resources(self.run_opts["raw_resources"])
            envvars = parse_utils.parse_env_vars(self.run_opts["envvars"])

            run = r_client.run(
                self.machine_type,
                run_type="jupyter",
                pip_packages=self.run_opts["pip_packages"],
                apt_packages=self.run_opts["apt_packages"],
                attached_resources=attached_resources,
                envvars=envvars,
                conda_file=self.run_opts["conda_file"],
                conda_name=self.run_opts["conda_env"])
            self.run_id = run.id
        except UnauthorizedRequest:
            # TODO(peter): Open up a stdin for the user to log in to
            exc_info = (
                SpellKernelException,
                SpellKernelException('Not logged in to Spell! Log in by running "spell login" in a terminal'),
                None,
            )
            self.handle_startup_exception(exc_info)
        except (ClientException, ParseException) as e:
            exc_info = (
                SpellKernelException,
                SpellKernelException(str(e)),
                None,
            )
            self.handle_startup_exception(exc_info)
        except Exception:
            self.handle_startup_exception(sys.exc_info())

    def track_run_status(self):
        try:
            r_client = runs_client.RunsClient(**self.api_opts)
            for entry in r_client.get_run_log_entries(str(self.run_id), follow=True, offset=0):
                if entry.get("status_event"):
                    self.run_status_queue.put(entry["status"])

            self._running = False
            if self.ssh_kernel is not None:
                self.ssh_kernel._running = False
        except ClientException as e:
            exc_info = (
                SpellKernelException,
                SpellKernelException(str(e)),
                None,
            )
            self.handle_startup_exception(exc_info)
        except Exception:
            self.handle_startup_exception(sys.exc_info())

    def wait_for_run(self):
        self.logger.info("Waiting for run, track progress with 'spell logs -f {}'".format(self.run_id))

        break_statuses = set(["running", "killing", "stopping", "failed"])
        while self._running:
            status = self.run_status_queue.get()
            self._log_to_cells("Run #{}: {}".format(self.run_id, status))
            if status in break_statuses:
                break

    def _send(self, stream, msg_type, content, parent=None, ident=None, flush=False):
        self.serializer.send(
            stream=self.local_streams[stream],
            msg_or_type=msg_type,
            parent=parent,
            ident=ident,
            content=content
        )
        if flush:
            self.local_streams[stream].flush()

    def _deserialize(self, raw_msg):
        idents, msg_list = self.serializer.feed_identities(raw_msg)
        msg = self.serializer.deserialize(msg_list)
        return idents, msg

    def _log_to_cells(self, log):
        content = {
            "name": "stdout",
            "text": log + "\n",
        }
        self._message_queue.put(content)

    def _dequeue_logs(self):
        while self._running:
            content = self._message_queue.get()
            with self._message_lock:
                if self._waiting_cell is not None and self._exception is None:
                    self._send("iopub", "stream", content,
                               parent=self._waiting_cell["parent"],
                               ident=self._waiting_cell["ident"],
                               flush=True)
                self._messages.append(content)
            self._message_queue.task_done()

    def _init_local_sockets(self, ctx):
        """ Set up the sockets that will be speaking directly to Jupyter """
        sockets = {
            "hb": ctx.socket(zmq.REP),
            "iopub": ctx.socket(zmq.PUB),
            "control": ctx.socket(zmq.ROUTER),
            "stdin": ctx.socket(zmq.ROUTER),
            "shell": ctx.socket(zmq.ROUTER),
        }
        for name, sock in sockets.items():
            transport = self.kernel_spec["transport"]
            ip = self.kernel_spec["ip"]
            port = self.kernel_spec["{}_port".format(name)]
            sock.bind("{}://{}:{}".format(transport, ip, port))

        streams = {
            name: zmqstream.ZMQStream(sock, self.ioloop)
            for name, sock in sockets.items()
        }
        return streams

    def _init_recv_sockets(self, ctx):
        """ Set up the sockets that will be speaking with the remote """
        sockets = {
            "hb": ctx.socket(zmq.REQ),
            "iopub": ctx.socket(zmq.SUB),
            "control": ctx.socket(zmq.DEALER),
            "stdin": ctx.socket(zmq.DEALER),
            "shell": ctx.socket(zmq.DEALER),
        }
        for name, sock in sockets.items():
            transport = self.kernel_spec["transport"]
            ip = self.kernel_spec["ip"]
            port = self.remote_ports[name]
            sock.connect("{}://{}:{}".format(transport, ip, port))
            if name == "iopub":
                # Subscribe iopub socket to all messages
                sock.setsockopt(zmq.SUBSCRIBE, b'')

        streams = {
            name: zmqstream.ZMQStream(sock, self.ioloop)
            for name, sock in sockets.items()
        }
        return streams

    def _init_dummy_sockets(self, ctx):
        """ Reserve local sockets so we don't disturb anything running locally when we forward traffic """
        sockets = {
            "hb": ctx.socket(zmq.REP),
            "iopub": ctx.socket(zmq.PUB),
            "control": ctx.socket(zmq.ROUTER),
            "stdin": ctx.socket(zmq.ROUTER),
            "shell": ctx.socket(zmq.ROUTER),
        }
        ports = {}
        for name, sock in sockets.items():
            transport = self.kernel_spec["transport"]
            ip = self.kernel_spec["ip"]
            port = sock.bind_to_random_port("{}://{}".format(transport, ip))
            ports[name] = port
        return sockets, ports

    def _build_ssh_config(self):
        ssh_config = {
            "port": self.ssh_port,
            "user": str(self.run_id),
            "key_paths": self.keys,
            "options": [
                "ServerAliveInterval=30",
                # TODO(peter): Use StrictHostKeyChecking
                "StrictHostKeyChecking=no",
            ],
        }
        return ssh_config

    def _build_ssh_connection_info(self):
        connection_info = copy.deepcopy(self.kernel_spec)
        for name, port in self.remote_ports.items():
            key = "{}_port".format(name)
            connection_info[key] = port
        return connection_info


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("connection_file")
    parser.add_argument("--machine-type", required=True)
    parser.add_argument("--spell-dir", help=argparse.SUPPRESS,
                        default=default_spell_dir())
    parser.add_argument("--api-url", help=argparse.SUPPRESS,
                        default="https://api.spell.run")
    parser.add_argument("--api-version", help=argparse.SUPPRESS,
                        default="v1")
    parser.add_argument("--ssh-host", help=argparse.SUPPRESS,
                        default="ssh.spell.run")
    parser.add_argument("--ssh-port", help=argparse.SUPPRESS,
                        default=22, type=int)
    parser.add_argument("--key", action="append", default=[])
    parser.add_argument("--pip", dest="pip_packages", action="append", default=[])
    parser.add_argument("--apt", dest="apt_packages", action="append", default=[])
    parser.add_argument("--conda-env")
    parser.add_argument("--conda-file")
    parser.add_argument("--env", dest="envvars", action="append", default=[])
    parser.add_argument("--mount", dest="raw_resources", action="append", default=[])

    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.connection_file) as cf:
        kernel_spec = json.load(cf)

    config_handler = ConfigHandler(args.spell_dir)
    try:
        config_handler.load_config_from_file()
        token = config_handler.config.token
        username = config_handler.config.user_name
    except ConfigException:
        token = ""
        username = ""

    api_opts = {
        "token": token,
        "base_url": args.api_url,
        "version_str": args.api_version,
    }

    run_opts = {
        "pip_packages": args.pip_packages,
        "apt_packages": args.apt_packages,
        "conda_env": args.conda_env,
        "conda_file": args.conda_file,
        "envvars": args.envvars,
        "raw_resources": args.raw_resources,
    }
    sk = SpellKernel(args.machine_type,
                     args.ssh_host,
                     args.ssh_port,
                     api_opts,
                     run_opts,
                     kernel_spec,
                     username=username,
                     keys=args.key)
    sk.initial_setup()
    # TODO(peter): Clean this up
    if not sk._running:
        return
    sk.wait_for_run()
    if not sk._running:
        return
    sk.ssh_setup()


if __name__ == "__main__":
    main()
