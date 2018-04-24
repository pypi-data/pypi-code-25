"""
This script will record key Linux OS parameters to a log file
It will record:
 a. Results of a ping to www.google.com
 b. If above result is false, then results of a ping to 8.8.8.8 and ping to the default gateway
 c. total cpu, mem, swap, dis space usage as a percentage
 d. whether the Ardexa service is running (true/false)
 e. if CPU exceeds 60%, dump the top 4 processes by CPU usage
 f. if MEM exceeds 5%, dump the top 4 processes by MEM usage

It will dump a log entry every 2 minutes to /opt/ardexa/black-box/logs
Any dumps where MEM or CPU are exceeded will go to: /opt/ardexa/black-box/dumps

Usage: sudo ardexa_black_box

For use on Linux systems
"""

# Copyright (c) 2018 Ardexa Pty Ltd
#
# This code is licensed under the MIT License (MIT).
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

from __future__ import print_function
import time
from subprocess import Popen, PIPE, STDOUT
import os
import datetime
import requests
import dns.resolver

GOOGLE_DNS = "8.8.8.8"
ARDEXA_BROKER = "broker.ardexa.com"
DEBUG = 1
ARDEXA_PIDFILE = "/var/run/ardexa.pid"
GOOD = "good"
BAD = "bad"
LOG_DIR = '/var/log/'
LOG_FILE = 'ardexa-black-box.log'
DUMP_FILE = 'ardexa-black-box-dumps.log'
AGENT_URL = "http://localhost:1818"
RESOLV_CONF = "/etc/resolv.conf"

#~~~~~~~~~~~~~~~~  START FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_top_cpu():
    """Get the top 4 CPU usage processes"""
    # ps aux --sort -pcpu | head
    proc_ps = Popen(['ps', 'aux', '--sort', '-pcpu'], stdout=PIPE, stderr=STDOUT)
    output = proc_ps.communicate()[0], proc_ps.stdout
    response = output[0]
    if DEBUG > 1:
        print("ps aux --sort -pcpu.. command: ", response)
    # Only get the top 4 lines
    count = 0
    result = '\n---------------------\nResults of ps aux --sort -pcpu command...\n'
    for line in response.splitlines():
        result = result + line +'\n'
        count = count + 1
        if count > 4:
            break

    # include a datetime stamp
    date_str = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    result = result + '\nDatetime: ' + date_str + '\n---------------------\n\n'
    # return the whole response
    return result

def get_top_swap():
    """Get the top 4 MEM usage processes"""
    # ps aux --sort -rss | head
    proc_ps = Popen(['ps', 'aux', '--sort', '-rss'], stdout=PIPE, stderr=STDOUT)
    output = proc_ps.communicate()[0], proc_ps.stdout
    response = output[0]
    if DEBUG > 1:
        print("ps aux --sort -rss.. command: ", response)
    # Only get the top 4 lines
    count = 0
    result = '\n---------------------\nResults of ps aux --sort -rss command...\n'
    for line in response.splitlines():
        result = result + line +'\n'
        count = count + 1
        if count > 4:
            break

    # include a datetime stamp
    date_str = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    result = result + '\nDatetime: ' + date_str + '\n----------------------\n\n'
    # return the whole response
    return result


def get_default_gateway():
    """Retrieve the default gateway"""
    # get 'df' based on '/' filesystem
    route = Popen(['route', '-n'], stdout=PIPE, stderr=STDOUT)
    output = route.communicate()[0], route.stdout
    response = output[0]
    if DEBUG > 1:
        print("route -n commnand: ", response)
    default_gateway = ""
    for line in response.splitlines():
        # Want the line that matches 'UG'
        if line.find("UG") != -1:
            # split on spaces
            items = line.split()
            default_gateway = items[1]

    return default_gateway


def get_diskspace():
    """Retrieve the used diskspace of the system"""
    # get 'df' based on '/' filesystem
    proc_df = Popen(['df', '-h', '/'], stdout=PIPE, stderr=STDOUT)
    output = proc_df.communicate()[0], proc_df.stdout
    response = output[0]
    if DEBUG > 1:
        print("Diskspace: ", response)
    diskspace_raw = ""
    for line in response.splitlines():
        # Want the line that DOESN'T match 'Filesystem'
        if line.find("Filesystem") == -1:
            items = line.split()
            diskspace_raw = items[4]

    diskspace = diskspace_raw.strip('%')
    return diskspace


def check_ip_ping(hostname):
    """This function will ping a hostname (IP or DNS)"""
    # Single ping only, no timeout
    ping = Popen(['ping', '-c', '1', hostname], stdout=PIPE, stderr=STDOUT)
    ret_code = ping.communicate()[0], ping.returncode
    response = ret_code[1]
    if DEBUG > 1:
        print("Pinging: ", hostname, " Return Code: ", ret_code[1])

    # return true/false
    if response == 0:
        status = GOOD
    else:
        status = BAD

    return status


def get_usage_percent():
    """Get CPU, MEM and SWAP usage"""
    # Run the top command in batch mode, and take 2 iterations
    usage = Popen(['top', '-b', '-n', '2'], stdout=PIPE, stderr=STDOUT)
    output = usage.communicate()[0], usage.stdout
    output_str = output[0]
    # there are 2 readings. Get the highest
    cpu_usage = -99.9
    mem_usage = -99.9
    swap_usage = -99.9

    for line in output_str.splitlines():
        if line.find("%Cpu(s)") != -1:
            if DEBUG > 1:
                print("CPU: ", line)
            cpu_usage_ex = extract_cpu_usage(line)
            if cpu_usage_ex > cpu_usage:
                cpu_usage = cpu_usage_ex

    mem_usage = extract_meminfo()
    swap_usage = extract_swapinfo()

    return cpu_usage, mem_usage, swap_usage


def extract_cpu_usage(cpu_line):
    """This will retrieve the CPU usage for system and user from a top line"""
    items = cpu_line.split()
    # convert items [1] and [3] into float and add them
    try:
        user = float(items[1])
        system = float(items[3])
        cpu_usage = user + system
    except:
        cpu_usage = -99.8

    return cpu_usage


def extract_meminfo():
    """This will extract memory usage from /proc/meminfo"""
    mem_total = 0
    mem_free = 0
    # open /proc/meminfo
    procinfo = open("/proc/meminfo", "r")
    for line in procinfo:
        line = line.strip()
        if line.find("MemTotal") != -1:
            items = line.split()
            mem_total = int(items[1])
            if DEBUG > 1:
                print(" Mem Total: ", mem_total)

        if line.find("MemFree") != -1:
            items = line.split()
            mem_free = int(items[1])
            if DEBUG > 1:
                print(" Mem Free: ", mem_free)

    procinfo.close()
    if mem_free != 0 and mem_total != 0:
        mem_usage = float(mem_total - mem_free)/ float(mem_total)
    else:
        mem_usage = 0

    if DEBUG > 1:
        print("mem usage: ", mem_usage)

    return mem_usage


def extract_swapinfo():
    """This will extract swap usage from /proc/meminfo"""
    swap_total = 0
    swap_free = 0
    # open /proc/meminfo
    procinfo = open("/proc/meminfo", "r")
    for line in procinfo:
        line = line.strip()
        if line.find("SwapTotal") != -1:
            items = line.split()
            swap_total = int(items[1])
            if DEBUG > 1:
                print(" Swap Total: ", swap_total)

        if line.find("SwapFree") != -1:
            items = line.split()
            swap_free = int(items[1])
            if DEBUG > 1:
                print(" Swap Free: ", swap_free)

    procinfo.close()
    if swap_free != 0 and swap_total != 0:
        swap_usage = float(swap_total - swap_free)/ float(swap_total)
    else:
        swap_usage = 0

    if DEBUG > 1:
        print("swap usage: ", swap_usage)

    return swap_usage


def check_ardexa_pid():
    """Check that the ardexa service is running"""

    # Check PID exists and see if the PID is running
    if os.path.isfile(ARDEXA_PIDFILE):
        pidfile_handle = open(ARDEXA_PIDFILE, 'r')
        try:
            pid = int(pidfile_handle.read())
            os.kill(pid, 0)
        except:
            return False

        pidfile_handle.close()
        return True
    return False


def write_log(log_directory, log_file, header, logline):
    """This function logs the data to a file"""
    write_header = False
    # Make sure the logging directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    full_path = os.path.join(log_directory, log_file)

    if DEBUG > 1:
        print("FULL PATH: ", full_path)

    # If the file doesn't exist, annotate that a header must be written
    if not os.path.isfile(full_path):
        if DEBUG > 1:
            print("file doesn't exist: ", full_path)
        write_header = True


    # Now create (or open) the file and write to it
    if DEBUG > 1:
        print("Writing the line: ", logline)

    write_file = open(full_path, "a")
    if write_header:
        write_file.write(header)
    write_file.write(logline)
    write_file.close()


def nslookup_ardexa():
    """This will return True if it can ping Ardexa Broker using Google DNS Server"""
    resolver = dns.resolver.Resolver()
    # 8.8.8.8 is Google's public DNS server
    resolver.nameservers = [GOOGLE_DNS]

    try:
        resolver.query(ARDEXA_BROKER, 'A')
        status = GOOD
    except:
        status = BAD

    return status


def get_agent_stats():
    """This gets the new agent stats. Will not work for any agent that is 1.10.0 or below"""
    agent_state = {}

    try:
        response = requests.get(AGENT_URL)
        agent_state = response.json()
    except:
        pass

    return agent_state


def log_resolv_conf():
    """This function will copy the resolv.conf file"""

    if DEBUG > 1:
        print("Taking a copy of resolv.conf")
    result = '\n---------------------\nContents of resolv.conf...\n'
    with open(RESOLV_CONF, 'r') as resolv_file:
        contents = resolv_file.read()

    result += contents

    # include a datetime stamp
    date_str = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    result += '\nDatetime: ' + date_str + '\n----------------------\n\n'

    # Dump (log) the DUMP FILE
    write_log(LOG_DIR, DUMP_FILE, "", result)


def cli():
    """The main function"""
    dns_ping_result = "no attempt"
    ip_ping_result = "no attempt"
    default_gateway_ping = "no attempt"
    ardexa_check = False
    nslook_result = "no attempt"
    run_state = "not retrieved"
    cloud_connection = "not retrieved"
    msg_count = "not retrieved"
    loop_count = "not retrieved"
    core_loop_state = "not retrieved"
    comm_loop_state = "not retrieved"
    core_ticker = "not retrieved"
    comm_ticker = "not retrieved"
    msg_cache = "not retrieved"

    # Check Ardexa Broker Ping
    dns_ping_result = check_ip_ping(ARDEXA_BROKER)

    # If Ardexa Broker could not be pinged, then try an IP ping and ping the gateway
    if dns_ping_result == BAD:
        # Check IP Ping
        ip_ping_result = check_ip_ping(GOOGLE_DNS)
        # and ping the gateway
        gateway = get_default_gateway()
        default_gateway_ping = check_ip_ping(gateway)
        # NS Lookup the Ardexa Broker
        nslook_result = nslookup_ardexa()
        # dump the contents of resolv.conf to file
        log_resolv_conf()
    else:
        # If this is the first run of the day, then dump the contents of resolv.conf to file
        now = datetime.datetime.now()
        minute = now.minute
        hour = now.hour
        if DEBUG:
            print("Current hour: ", hour)
            print("Current minute: ", minute)

        if hour == 0 and minute >= 1 and minute <= 15:
            log_resolv_conf()

    cpu_usage, mem_usage, swap_usage = get_usage_percent()
    diskspace = get_diskspace()
    ardexa_check = check_ardexa_pid()
    agent_state = get_agent_stats()

    # Call down the agent stats. If they exist
    if "run_state" in agent_state:
        run_state = agent_state["run_state"]
    if "cloud_connection" in agent_state:
        cloud_connection = agent_state["cloud_connection"]
    if "msg_count" in agent_state:
        msg_count = agent_state["msg_count"]
    if "loop_count" in agent_state:
        loop_count = agent_state["loop_count"]
    if "core_loop_state" in agent_state:
        core_loop_state = agent_state["core_loop_state"]
    if "comm_loop_state" in agent_state:
        comm_loop_state = agent_state["comm_loop_state"]
    if "core_ticker" in agent_state:
        core_ticker = agent_state["core_ticker"]
    if "comm_ticker" in agent_state:
        comm_ticker = agent_state["comm_ticker"]
    if "msg_cache" in agent_state:
        msg_cache = agent_state["msg_cache"]


    if DEBUG > 0:
        print("CPU usage: ", cpu_usage)
        print("MEM usage: ", mem_usage)
        print("SWAP usage: ", swap_usage)
        print("Diskspace: ", diskspace)
        print("8.8.8.8 IP ping returned: ", ip_ping_result)
        print("broker.ardexa.com ping returned: ", dns_ping_result)
        print("Ardexa running: ", ardexa_check)
        print("Default Gateway ping: ", default_gateway_ping)
        print("ardexa.broker.com nslookup using 8.8.8.8: ", nslook_result)
        print("Agent run state: ", run_state)
        print("Agent cloud connection: ", cloud_connection)
        print("Agent message count: ", msg_count)
        print("Agent loop count: ", loop_count)
        print("Agent core loop state: ", core_loop_state)
        print("Agent comm loop state: ", comm_loop_state)
        print("Agent core ticker: ", core_ticker)
        print("Agent comm ticker: ", comm_ticker)
        print("Agent message cache: ", msg_cache)

    # if CPU usage is greater than 60%, dump the top 4 procs by mem and CPU
    # Test this on Linux as follows: sudo stress --cpu  4 --timeout 20 (sudo apt-get install stress)
    if cpu_usage > 60.0:
        response = get_top_cpu()
        if DEBUG > 1:
            print("CPU Greater than 60%: ", response)
        # Dump (log) the line
        write_log(LOG_DIR, DUMP_FILE, "", response)

    # if SWAP usage is greater than 5%, dump the top 4 procs by mem and CPU
    # Test this on Linux as follows: sudo stress --cpu  4 --timeout 20 (sudo apt-get install stress)
    if swap_usage > 15.0:
        response = get_top_swap()
        if DEBUG > 1:
            print("SWAP Greater than 5%: ", response)
        # Dump (log) the line
        write_log(LOG_DIR, DUMP_FILE, "", response)


    # Format mem_usage and swap_usage
    mem_usage_str = format(mem_usage*100, '.1f')
    swap_usage_str = format(swap_usage*100, '.1f')

    # Formulate the log line
    date_str = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    # pylint: disable=line-too-long
    header = "# Datetime, CPU usage (%), MEM usage (%), SWAP usage (%), DISK usage (%), Ardexa Broker DNS ping, 8.8.8.8 IP ping, Gateway ping, NS Lookup broker.ardexa.com using 8.8.8.8, Ardexa running, Agent run state, Agent cloud connection, Agent message count, Agent loop count, Agent core loop state, Agent comm loop state, Agent core ticker, Agent comm ticker, Agent message cache\n"
    log_line = date_str + "," + str(cpu_usage) + "," + mem_usage_str + "," + swap_usage_str + "," + str(diskspace) + "," + dns_ping_result + "," + ip_ping_result + "," + default_gateway_ping + "," + nslook_result + "," + str(ardexa_check) + "," +  str(run_state) + "," +  str(cloud_connection) + "," + str(msg_count) + "," + str(loop_count) + "," + str(core_loop_state) + "," + str(comm_loop_state) + "," + str(core_ticker) + "," + str(comm_ticker) + "," + str(msg_cache) + '\n'
    # pylint: enable=line-too-long

    # Log the data
    write_log(LOG_DIR, LOG_FILE, header, log_line)
