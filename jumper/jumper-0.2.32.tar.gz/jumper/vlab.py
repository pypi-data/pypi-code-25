"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function
from builtins import input
import os
import errno
import subprocess
from common import VlabException
import hashlib
import sys
from time import sleep
from shutil import copyfile
import platform
import requests
from distutils.version import LooseVersion
from __version__ import __version__ as jumper_current_version
import json
from termcolor import colored
from terminaltables import SingleTable
from terminaltables import AsciiTable
import threading
from .timeout_dec import timeout
from .common import TimeoutException
from .common import EmulationError
from .common import MissingFileError
from .common import ArgumentError
from .common import TranspilerError
import tarfile

from .jemu_bsp_parser import JemuBspParser
from .jemu_gpio import JemuGpio
from .jemu_connection import JemuConnection
from .jemu_web_api import JemuWebApi
from .jemu_interrupts import JemuInterrupts
from .jemu_uart_json import JemuUartJson as JemuUart

config_file_name = 'config.json'
if 'JUMPER_STAGING' in os.environ:
    config_file_name = 'config.staging.json'
if 'JUMPER_STAGING_INBAR' in os.environ:
    config_file_name = 'config.inbar.json'
JUMPER_DIR = os.path.join(os.path.expanduser('~'), '.jumper')
DEFAULT_CONFIG = os.path.join(JUMPER_DIR, config_file_name)
MISSING_CONFIG_FILE_ERROR1 = "Token id was not found."
MISSING_CONFIG_FILE_ERROR2 = "\nTo obtain a token file, create an account in this link " \
                             "- https://vlab.jumper.io/ and follow the steps."
MISSING_CONFIG_FILE_ERROR3 = "\nAfter opening an account, use one of the following steps:" \
                             "\n1. Use '--token' flag with your secret token." \
                             "\n2. Make sure you have a config file in: '/home/user/.jumper/config.json'"
CORE_LINUX_OS = "linux"
CORE_WINDOWS_OS1 = "win"
CORE_WINDOWS_OS2 = "cygwin"
CORE_MAC_OS = "darwin"

JEMU_LINUX_DIR = "jemu-linux"
JEMU_MAC_DIR = "jemu-mac"
JEMU_WINDOWS_DIR = "jemu-windows"

DOCKER_JUMPER_VLAB_MESSAGE = "jumperio/jumper-vlab"
DOCKER_VLAB__GCC_ARM_MESSAGE = "jumperio/vlab-gcc-arm"
HERE = os.path.abspath(os.path.dirname(__file__))


class Vlab(object):
    """
    The main class for using Jumper Virtual Lab

    :param working_directory: The directory that holds the board.json abd scenario.json files for the virtual session
    :param config_file: Config file holding the API token (downloaded from https://vlab.jumper.io)
    :param gdb_mode: If True, a GDB server will be opened on port 5555
    :param sudo_mode: If True, firmware can write to read-only registers. This is useful for injecting a mock state to the hardware.
    :param registers_trace: Adds a trace for CPU registers values before every CPU instruction.
    :param functions_trace: Adds a trace for the the functions that are being executed (requires a .out or .elf file)
    :param interrupts_trace: Adds a trace for interrupts handling.
    :param trace_output_file: If traces_list is not empty, redirects the trace from stdout to a file.
    :param print_uart: If True UART prints coming from the device will be printed to stdout or a file
    :param uart_output_file: If print_uart is True, sets the UART output file. Default is stdout.
    :param token: The API token to be used for authentication. If not specified, the token in ~/.jumper/config.json will be used.
    """
    if os.environ.get('JEMU_DIR') is None:
        _transpiler_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'jemu'))
    else:
        _transpiler_dir = os.path.abspath(os.environ['JEMU_DIR'])

    _jemu_build_dir = os.path.abspath(os.path.join(_transpiler_dir, 'emulator', '_build'))
    _instructions_tgz_src = os.path.join(_jemu_build_dir, 'instructions_lib.tgz')

    _INT_TYPE = "interrupt_type"

    _DESCRIPTION = "description"
    _TYPE_STRING = "type"
    _BKPT = "bkpt"
    _VALUE_STRING = "value"
    _EXAMPLES_HASH_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'examples_hash_list.json'))

    def _load_example_hash_map(self):
        try:
            return json.load(open(self._EXAMPLES_HASH_FILE))
        except Exception as e:
            print (e.message)
            return {}

    @staticmethod
    def _get_latest_version(name):
        url = "https://pypi.python.org/pypi/{}/json".format(name)
        try:
            return list(reversed(sorted(requests.get(url).json()["releases"], key=LooseVersion)))[0]
        except Exception as e:
            return None

    @staticmethod
    def _print_update_to_screen(jumper_latest_version, jumper_current_version):
        if 'DOCKER_JUMPER' in os.environ:
            message = Vlab._get_update_message_for_docker(jumper_latest_version, jumper_current_version, DOCKER_JUMPER_VLAB_MESSAGE)
        elif 'DOCKER_JUMPER_EXAMPLES' in os.environ:
            message = Vlab._get_update_message_for_docker(jumper_latest_version, jumper_current_version, DOCKER_VLAB__GCC_ARM_MESSAGE)
        else:
            message = Vlab._get_update_message(jumper_latest_version, jumper_current_version)

        table_data = [[message]]
        if sys.platform.startswith(CORE_WINDOWS_OS1) or sys.platform.startswith(CORE_WINDOWS_OS2):
            table = AsciiTable(table_data)
        else:
            table = SingleTable(table_data)
        table.padding_left = 2
        table.padding_right = 2
        print()
        print(table.table.encode('utf-8'))
        print()

    @staticmethod
    def _get_update_message(jumper_latest_version, jumper_current_version):
        if sys.platform.startswith(CORE_WINDOWS_OS1) or sys.platform.startswith(CORE_WINDOWS_OS2):
            update_message = "Update available from {0}".format(jumper_current_version) + " to " + jumper_latest_version
            how_to_updtae_message = "\n  Run pip install jumper --upgrade to update"
        else:
            update_message = "Update available {0} ".format(jumper_current_version) + u'\u2192' + colored(
                " " + jumper_latest_version, 'green', attrs=['bold'])
            how_to_updtae_message = "\n  Run " + colored(" sudo pip install jumper --upgrade ", "blue",
                                                         attrs=['bold']) + "to update"

        return update_message + how_to_updtae_message

    @staticmethod
    def _get_update_message_for_docker(jumper_latest_version, jumper_current_version, docker_name):
        update_message = "Update available {0} ".format(jumper_current_version) + u'\u2192' + colored(
            " " + jumper_latest_version, 'green', attrs=['bold'])
        how_to_updtae_message = "\n  You can either run: " + colored("pip install jumper --upgrade ", "blue",
            attrs=['bold']) + "to update" + "\n  or exit docker and pull this container: " + colored(
            "docker pull " + docker_name + " ", "blue", attrs=['bold'])

        return update_message + how_to_updtae_message

    @classmethod
    def check_sdk_version(cls):
        jumper_latest_version = Vlab._get_latest_version("jumper")
        if jumper_latest_version:
            if LooseVersion(jumper_current_version) < LooseVersion(jumper_latest_version):
                Vlab._print_update_to_screen(jumper_latest_version, jumper_current_version)

    @staticmethod
    def get_jemu_path():
        jemu_dest = None
        if sys.platform.startswith(CORE_LINUX_OS):
            jemu_dest = os.path.join(HERE, 'jemu', JEMU_LINUX_DIR, 'jemu')
        elif sys.platform.startswith(CORE_MAC_OS):
            jemu_dest = os.path.join(HERE, 'jemu', JEMU_MAC_DIR, 'jemu')
        elif sys.platform.startswith(CORE_WINDOWS_OS1) or sys.platform.startswith(CORE_WINDOWS_OS2):
            jemu_dest = os.path.join(HERE, 'jemu', JEMU_WINDOWS_DIR, 'jemu.exe')
        return jemu_dest

    def _get_jemu_version(self):
        jemu_version = None
        if os.path.isfile(self._jemu_path):
            jemu_cmd = [self._jemu_path, '-v']
            try:
                jemu_version = subprocess.check_output(jemu_cmd, cwd=self._working_directory).rstrip()
            except:
                pass
        if jemu_version is None:
            raise VlabException("Could not get jemu version", 7)
        return jemu_version

    def __init__(
            self,
            working_directory=None,
            config_file=None,
            gdb_mode=False,
            sudo_mode=False,
            registers_trace=False,
            functions_trace=False,
            interrupts_trace=False,
            trace_output_file=None,
            print_uart=False,
            uart_output_file=None,
            token=None,
            debug_peripheral=False
    ):
        args = locals()
        self.check_sdk_version()
        self._working_directory = os.path.abspath(working_directory) if working_directory else self._transpiler_dir
        self._working_directory_dot_jumper = os.path.join(self._working_directory, '.jumper')
        self._gdb_mode = gdb_mode
        self._sudo_mode = sudo_mode
        self._jemu_process = None
        self._debug_peripheral = debug_peripheral
        self._was_start = False
        self._local_jemu = True if (('LOCAL_JEMU' in os.environ) or ('JEMU_LOCAL' in os.environ)) else False
        self._jemu_server_address = "localhost"
        self._instructions_lib = os.path.join(self._working_directory_dot_jumper, "instructions.so")
        self._program_bin = os.path.join(self._working_directory_dot_jumper, 'program.bin')
        self._instructions_tgz = os.path.join(self._working_directory_dot_jumper, 'instructions_lib.tgz')
        self._cache_file = os.path.join(self._working_directory_dot_jumper, 'firmware.cache.sha1')
        self.remove_pty_if_exist()
        self._jemu_connection = JemuConnection(self._jemu_server_address)
        self._uart = JemuUart(self)
        self._registers_trace = registers_trace
        self._functions_trace = functions_trace
        self._interrupts_trace = interrupts_trace
        self._trace_output_file = trace_output_file
        self._print_uart = print_uart
        self._uart_output_file = uart_output_file
        self._jemu_debug = True if 'JEMU_DEBUG' in os.environ else False
        self._jemu_port = 8000 if self._jemu_debug else 0
        self._on_bkpt = None
        self._return_code = None
        self._jemu_connection.register(self.receive_packet)
        self._jemu_path = Vlab.get_jemu_path()
        self._jemu_interrupt = JemuInterrupts()
        self._threads = []
        self._stdout_thread = None
        self._peripherals_json_parser = None
        self._build_components_methods()
        self._jemu_gpio = JemuGpio()
        self._firmware = None
        self._new_signature = None
        self._web_api = None

        try:
            if not os.path.exists(self._working_directory_dot_jumper):
                os.makedirs(self._working_directory_dot_jumper)

            self._init_web_app_with_token(token, config_file)
            self._web_api.add_event({'event': 'start run'})

            user_os = sys.platform
            if not self._local_jemu and not (self._jemu_path and (user_os.startswith(CORE_LINUX_OS) or user_os.startswith(CORE_WINDOWS_OS1))):
                self._web_api.add_event({'event': 'os error', "labels": {'os': user_os}})
                raise VlabException("Jumper Virtual Lab is currently only supported on Ubuntu 16.04 and Windows. Use one of these operating systems or our ready-to-use Docker image.\nHead to https://docs.jumper.io/docs/rundocker.html to learn more.", 6)

            # delete self key
            args.pop('self', None)
            # send flags events
            for key in args.keys():
                if args[key]:
                    self._web_api.add_event({'event': 'jumper run', 'labels': {'parameter': str(key)}})

            self._examples_hash_map = self._load_example_hash_map()

        except (VlabException, KeyboardInterrupt) as e:
            self.stop()
            raise e

    def _send_gpio_event(self):
        self._web_api.add_event({'event': 'jumper run', 'labels': {'parameter': 'gpio'}})

    def _send_stop_after_event(self):
        self._web_api.add_event({'event': 'jumper run', 'labels': {'parameter': 'stop_after'}})

    def _init_web_app_with_token(self, token, config_file):
        secret_token = token
        if not secret_token:
            config_file = config_file or DEFAULT_CONFIG
            if not os.path.isfile(config_file):
                self._missing_config_file()
            with open(config_file) as config_data:
                config = json.load(config_data)
            if 'token' in config:
                secret_token = config['token']

        if secret_token is not None:
            try:
                self._web_api = JemuWebApi(jumper_token=secret_token, local_jemu=self._local_jemu)
            except requests.ConnectionError as e:
                if os.path.isfile(self._instructions_lib) and os.path.isfile(self._program_bin) and os.path.isfile(self._jemu_path):
                    print("Could not connect to server, version will not be updated: " + e.message)
                    self._web_api = None
                else:
                    raise VlabException("Could not connect to server: " + e.message, 7)
        else:
            self._missing_config_file()

    @staticmethod
    def _silent_remove_file(filename):
        try:
            if os.path.isfile(filename):
                os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def _missing_config_file(self):
        self.stop()
        bold_message = colored(MISSING_CONFIG_FILE_ERROR2, attrs=['bold'])
        error_message = ''.join([MISSING_CONFIG_FILE_ERROR1, bold_message, MISSING_CONFIG_FILE_ERROR3])
        raise MissingFileError(error_message)

    def _valid_file_existence(self, file_path):
        if not os.path.isfile(file_path):
            raise MissingFileError("Failed to open binary file (at: '" + file_path + "')")

    @property
    def uart(self):
        """
        The main UART device for the Virtual Lab session

        :return: :class:`~jumper.jemu_uart.JemuUart`
        """
        return self._uart

    @property
    def gpio(self):
        return self._jemu_gpio

    @property
    def interrupts(self):
        return self._jemu_interrupt

    # @property
    # def interrupt_type(self):
    #     return self._INT_TYPE

    def _build_components_methods(self):
        peripherals_json = os.path.join(self._working_directory, "peripherals.json")
        bsp_json = os.path.join(self._working_directory, "bsp.json")
        default_bsp_json = os.path.join(os.path.dirname(__file__), "default_bsp.json")
        board_json = os.path.join(self._working_directory, "board.json")
        default_board_json = os.path.join(os.path.dirname(__file__), "default_board.json")

        if os.path.isfile(board_json):
            components_list = self._parse_bsp_json(board_json)
        elif os.path.isfile(bsp_json):
            components_list = self._parse_bsp_json(bsp_json)
        elif os.path.isfile(peripherals_json):
            raise VlabException('peripherals.json format is not supported anymore', 7)
        else:
            if os.path.isfile(default_board_json):
                components_list = self._parse_bsp_json(default_board_json)
            else:
                components_list = self._parse_bsp_json(default_bsp_json)

        for component in components_list:
            setattr(self, component["name"], component["obj"])

    def _parse_bsp_json(self, bsp_path):
        bsp_json_parser = JemuBspParser(bsp_path)
        return bsp_json_parser.get_components(self._jemu_connection)

    @staticmethod
    def _get_file_signature(file_path):
        sha1 = hashlib.sha1()

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)

        return sha1.hexdigest()

    def _read_file_signature_backup(self):
        data = ''
        if os.path.isfile(self._cache_file):
            if os.path.isfile(self._instructions_lib):
                with open(self._cache_file, 'r') as f:
                    data = f.read().replace('\n', '')
            else:
                os.remove(self._cache_file)

        return data

    def _write_file_signature_backup(self):
        with open(self._cache_file, 'w+') as f:
            f.write(self._new_signature)

    def _unzip_instructions_lib(self):
        try:
            tar = tarfile.open(self._instructions_tgz)
            tar.extractall(path=self._working_directory_dot_jumper)
            tar.close()
        except Exception:
            raise MissingFileError('Error: Could not open jemu file. Please contact us at support@jumper.io with a copy of this trace text')

        if os.path.isfile(self._instructions_lib):
            os.chmod(self._instructions_lib, 0o777)
        if os.path.isfile(self._program_bin):
            os.chmod(self._program_bin, 0o777)
        os.remove(self._instructions_tgz)

    def load(self, file_path):
        """
        Loads firmware to a virtual device and initialises a Virtual Lab session.
        Use :func:`~jumper.Vlab.start()` to start an emulation after this method was called.

        :param file_path: Path for a firmware file (supported extensions are bin, out, elf, hex)
        """
        ext = [".bin", ".out", ".elf", ".hex"]
        if not file_path.endswith(tuple(ext)):
            raise ArgumentError('Invalid file extension - supported extensions are bin, out, elf, hex')

        file_path = os.path.abspath(file_path)
        self._valid_file_existence(file_path)
        self._firmware = file_path
        self._new_signature = self._get_file_signature(self._firmware)
        self._valid_file_existence(self._firmware)

        gen_new_so = self._is_should_gen_new_so()
        self._perform_silent_remove(gen_new_so)

        if self._local_jemu:  # load from local (development)
            self._load_from_local(gen_new_so)
        else:  # load from cloud
            self._load_so_from_cloud(gen_new_so)

        if gen_new_so and os.path.isfile(self._instructions_lib) and os.path.isfile(self._jemu_path):
            self._write_file_signature_backup()

    def _is_should_gen_new_so(self):
        gen_new_so = True
        prev_signature = self._read_file_signature_backup()
        if prev_signature == self._new_signature and os.path.isfile(self._program_bin):
            gen_new_so = False
        return gen_new_so

    def _perform_silent_remove(self, gen_new_so):
        if gen_new_so:
            self._silent_remove_file(self._cache_file)
            self._silent_remove_file(self._instructions_lib)

    def _load_from_local(self, gen_new_so):
        self._load_from_local_instructions(gen_new_so)
        self._load_from_local_jemu()

    def _load_from_local_instructions(self, gen_new_so):
        try:
            if gen_new_so:  # create new
                user_os = platform.system()
                transpiler_cmd = ["node", "index.js", "--bin", self._firmware, "--zip", "--os", user_os]
                subprocess.check_call(transpiler_cmd, stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'), cwd=self._transpiler_dir)
                copyfile(self._instructions_tgz_src, self._instructions_tgz)
                self._unzip_instructions_lib()
        except subprocess.CalledProcessError as e:
            raise TranspilerError("Transpiler failed with an error: " + e.message)

    def _load_from_local_jemu(self):
        try:
            if os.name != 'nt':
                make_cmd = ['npm', 'run', 'build-jemu']
                subprocess.check_call(make_cmd, cwd=self._transpiler_dir, stdout=open(os.devnull, 'w'),
                                      stderr=open(os.devnull, 'w'))
            else:  # run from win
                run_build_bat = os.path.join(self._transpiler_dir, 'emulator', 'jemu', 'build', 'build.bat')
                subprocess.check_call(run_build_bat, stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
        except subprocess.CalledProcessError as e:
            raise TranspilerError("Build jemu failed with an error: " + e.message)

    def _load_so_from_cloud(self, gen_new_so):
        filename = os.path.basename(self._firmware)
        if gen_new_so:   # create new
            if self._new_signature in self._examples_hash_map:
                self._web_api.add_event({'event': 'upload firmware', "labels": {'example': True, 'example_name': self._examples_hash_map[self._new_signature], 'filename': filename}})
            else:
                self._web_api.add_event({'event': 'upload firmware', "labels": {'example': False, 'filename': filename}})
            with open(self._firmware, 'rb') as data:
                jemu_version = self._get_jemu_version()
                self._web_api.get_archived_so_file(filename, data, self._instructions_tgz, jemu_version)
                self._unzip_instructions_lib()
        else:  # load from cache
            self._web_api.add_event({'event': 'using cached firmware', "labels": {'filename': filename}})

    def start(self, ns=None):
        """
        Starts the emulation

        :param ns: If provided, commands the virtual device to run for the amount of time given in ns and then halt.

            If this parameter is used, this function is blocking until the virtual devices halts,
            if None is given, this function is non-blocking.
        """
        if not os.path.isfile(self._jemu_path):
            raise MissingFileError(self._jemu_path + ' is not found')
        elif not os.access(self._jemu_path, os.X_OK):
            raise MissingFileError(self._jemu_path + ' is not executable')

        self._was_start = True

        jemu_cmd = self._build_jemu_cmd()

        def jemu_connection():
            @timeout(6)
            def wait_for_connection():
                while self._jemu_port == 0:
                    sleep(0.1)

                while not self._jemu_connection.connect(self._jemu_port):
                    sleep(0.1)
            try:
                wait_for_connection()
            except TimeoutException:
                self.stop()
                raise EmulationError("Error: Couldn't connect to Emulator. Please contact us at support@jumper.io with a copy of this trace text")
            if not self._jemu_connection.handshake(ns):
                raise EmulationError("Error: Couldn't connect to Emulator. Please contact us at support@jumper.io with a copy of this trace text")

            self._jemu_gpio.set_connection_manager(self._jemu_connection)
            self._jemu_interrupt.set_jemu_connection(self._jemu_connection)
            self._jemu_connection.register(self.receive_packet)

        if self._jemu_debug:
            input("Start a debugger with the following parameters:\n\
            cwd: {}\n\
            command: {}\n\
            Press Enter to continue...".format(self._working_directory, ' '.join(jemu_cmd))
                  )
            jemu_connection()
        else:
            try:
                self._jemu_process = subprocess.Popen(jemu_cmd, cwd=self._working_directory, stdout=subprocess.PIPE)
                if self._debug_peripheral:
                    input("In order to debug your peripheral attach to process"
                          " pid: {}\nPress enter after connection...".format(self._jemu_process.pid))
                sleep(0.3)
            except Exception as e:
                raise EmulationError(e.message)

            self._jemu_port = self._uart._uart_port = 0
            self._stdout_thread = threading.Thread(target=self._thread_stdout_function)
            self._stdout_thread.start()
            self._threads.append(self._stdout_thread)
            jemu_connection()

        try:
            self._uart.open()
        except TimeoutException:
            self.stop()
            raise EmulationError("Error: Uart doesn't exist. Please contact us at support@jumper.io with a copy of this trace text")

        self._jemu_connection.start()

    def _build_jemu_cmd(self):
        jemu_cmd = [self._jemu_path, '-w', '--sdk-port', str(self._jemu_port)]

        if self._gdb_mode:
            jemu_cmd.append('-g')
        if self._sudo_mode:
            jemu_cmd.append('-s')

        traces = []
        if self._registers_trace:
            traces.append('regs')
        if self._functions_trace:
            traces.append('functions')
            self._build_obj_dump_file(jemu_cmd)
        if self._interrupts_trace:
            traces.append('interrupts')
        traces_string = ','.join(traces) if len(traces) > 0 else None

        if traces_string:
            jemu_cmd.extend(['-t', traces_string])

        if self._trace_output_file:
            jemu_cmd.append('--trace-dest')
            jemu_cmd.append(self._trace_output_file)

        if self._print_uart:
            # print uart to file - jemu responsible
            if self._uart_output_file:
                jemu_cmd.append('-u')
                jemu_cmd.append(self._uart_output_file)

            # print uart to screen - sdk responsible
            else:
                self.uart.print_uart_to_screen()

        return jemu_cmd

    def _build_obj_dump_file(self, jemu_cmd):
        if not self._firmware.endswith('.out') and not self._firmware.endswith('.elf'):
            raise ArgumentError('Invalid file extension - for running functions trace, use out or elf file')

        # check if arm-none-eabi-objdump exists
        try:
            subprocess.check_call(['arm-none-eabi-objdump', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            raise VlabEnvironmentError('arm-none-eabi-objdump is required for generating the functions trace. Install the GCC ARM Embedded Toolchain or remove the functions argument to proceed.')

        # create dump file
        try:
            cmd = "arm-none-eabi-objdump -d " + self._firmware + " > objdump.txt"
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self._working_directory)
            p.wait()
            sleep(0.3)
        except Exception as e:
            raise EmulationError(e.message)

        jemu_cmd.extend(['--objdump', 'objdump.txt'])

    def _thread_stdout_function(self):
        self._assert_jemu_is_running()

        jemu_port_found = False
        uart_port_found = False

        while not (jemu_port_found and uart_port_found):
            line = self._jemu_process.stdout.readline()
            if line == '':
                return
            line_data = line.split(' ')

            if len(line_data) >= 2:
                if line_data[0] == 'port:':
                    self._jemu_port = line_data[1]
                    jemu_port_found = True
                elif line_data[0] == 'uart_port:':
                    self._uart._uart_port = line_data[1]
                    uart_port_found = True

    def stop(self):
        """
        Stops the Virtual Lab session.

        Opposing to halting the session, the virtual device cannot be resumed after a stop command.

        """
        if self._jemu_connection:
            self._jemu_connection.close()

        self.remove_pty_if_exist()

        if self._jemu_process and self._jemu_process.poll() is None:
            self._jemu_process.terminate()
            self._jemu_process.wait()
            self._return_code = 0

        self._stop_threads()
        self._uart = None
        self._jemu_connection = None

        if self._web_api:
            self._web_api.stop()

    def _stop_threads(self):
        for t in self._threads:
            if t.is_alive():
                t.join()

    def remove_pty_if_exist(self):
        uart_device_path = os.path.join(self._working_directory, 'uart')
        if not os.path.exists(uart_device_path):
            return

        if not os.path.islink(uart_device_path):
            raise Exception(uart_device_path + ' not symbolic link')

        os.unlink(uart_device_path)

    def run_for_ms(self, ms):
        """
        Starts or resumes the virtual device, the device will halt after the amount of time specified.

        This function is blocking until the virtual device has halted. Use this when the virtual device is stopped
        or halted.

        :param ms: Time to run in ms
        """
        self.run_for_us(ms * 1000)

    def run_for_us(self, us):
        """
        Starts or resumes the virtual device, the device will halt after the amount of time specified.

        This function is blocking until the virtual device has halted. Use this when the virtual device is stopped
        or halted.

        :param ms: Time to run in us
        """
        self.run_for_ns(us * 1000)

    def run_for_ns(self, ns):
        """
        Starts or resumes the virtual device, the device will halt after the amount of time specified.

        This function is blocking until the virtual device has halted. Use this when the virtual device is stopped
        or halted.

        :param ns: Time to run in ns
        """
        if not self._was_start:
            self.start(ns)
            self.SUDO.wait_until_stopped()
        else:
            self.SUDO.run_for_ns(ns)

    def stop_after_ms(self, ms):
        # """
        # Causes the virtual device to halt after the amount of time specified.
        # This function is non-blocking and does not cause the device to resume.
        #
        # Use this when the virtual device is halted.
        #
        # :param ms: Time to run in ms
        # """
        self.stop_after_ns(ms * 1000000)

    def stop_after_ns(self, ns):
        # """
        # Causes the virtual device to halt after the amount of time specified.
        # This function is non-blocking and does not cause the device to resume.
        #
        # Use this when the virtual device is halted.
        #
        # :param ns: Time to run in ns
        # """
        self.SUDO.stop_after_ns(ns)

    def resume(self):
        """
        Resumes a paused device.

        """
        self.SUDO.resume()

    def cancel_stop(self):
        self.SUDO.cancel_stop()

    def pause(self):
        """
        Pause the device.

        """
        self.run_for_ns(0)

    def on_interrupt(self, callback):
        """

        :param callback: The callback to be called when an interrupt is being handled. The callback will be called with callback(interrupt)
        """
        self._jemu_interrupt.on_interrupt([callback])

    def set_timer(self, ns, callback):
        self.SUDO.set_timer(ns, callback)

    def get_state(self):
        if not self._was_start:
            return "init"
        elif not self.is_running():
            return "stopped"
        return self.SUDO.get_state()

    def on_pin_level_event(self, callback):
        """
        Specifies a callback for a pin transition event.

        :param callback: The callback to be called when a pin transition occures. The callback will be called with callback(pin_number, pin_level)
        """
        self.gpio.on_pin_level_event(callback)

    def get_pin_level(self, pin_num):
        """
        Specifies get the pin level for a pin num.

        :param pin num: pin number id
        """
        return self.gpio.get_pin_level(pin_num)

    def on_bkpt(self, callback):
        """
        Sets a callback to be called when the virtual device execution reaches a BKPT assembly instruction.

        :param callback: The callback to be called. Callback will be called with callback(code)\
        where code is the code for the BKPT instruction.
        """
        self._on_bkpt = callback

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._DESCRIPTION] == self._BKPT:
            if self._on_bkpt is not None:
                bkpt_code = jemu_packet[self._VALUE_STRING]
                self._on_bkpt(bkpt_code)

    def is_running(self):
        """
        Checks if the virtual device has been started.

        :return: True if running or pause, False otherwise.
        """
        if not self._jemu_process:
            if self._jemu_debug:
                return True
            else:
                return False

        self._return_code = self._jemu_process.poll()
        return self._return_code is None

    def get_return_code(self):
        """
        Checks a return code from the device.

        :return:
            - 0 if device was stopped using the :func:`~stop()` method
            - Exit code from firmware if the Device exited using the jumper_sudo_exit_with_exit_code() \
            command from jumper.h
        """
        if not self._jemu_process:
            return None

        if self._return_code is None:
            self._return_code = self._jemu_process.poll()

        return self._return_code

    def _assert_jemu_is_running(self):
        if not self.is_running():
            raise EmulationError("Error: The Emulator is not running.")

    def get_device_time_ns(self):
        """
        How much time passed from beginning of the emulation.

        :return: Emulation time in nanoseconds.
        """
        return self.SUDO.get_device_time_ns()

    def get_device_time_us(self):
        """
        How much time passed from beginning of the emulation.

        :return: Emulation time in microseconds.
        """
        return self.get_device_time_ns() / 1000

    def get_device_time_ms(self):
        """
        How much time passed from beginning of the emulation.

        :return: Emulation time in milliseconds.
        """
        return self.get_device_time_us() / 1000

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *err):
        self._web_api.add_event({'event': 'stop run'})
        self.stop()

    def __del__(self):
        self.stop()

