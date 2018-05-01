"""
This script will query a single Phoenix Contact SOLARCHECK string monitor.
Usage: solarcheck_ardexa ip_address port rs485_addresses log_directory strings
Eg; solarcheck_ardexa get 192.168.1.2 502 14-21 /opt/ardexa 8
{IP Address} = IP address of the string combiner, eg; 192.168.1.2
{Port} = Modbus port, eg; 502
{RS485 Address(es)} = RS485 address or range of addresses, eg; 1-5 or 1,2,3 or 4 (for example)
{log directory} = logging directory, eg; /opt/ardexa/
{number of strings to query} = 3  (can query up to 8 strings)

For debug, use -v or -vv (very verbose)
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
import sys
import time
import os
from subprocess import Popen, PIPE
import click
import ardexaplugin as ap

PY3K = sys.version_info >= (3, 0)


START_REG = "1"
REGS_TO_READ = "87"


def write_line(line, ip_address, inverter_addr, string, base_directory, header_line, debug):
    """This will write a line to the base_directory
    Assume header and lines are already \n terminated"""
    # Write the log entry, as a date entry in the log directory
    date_str = (time.strftime("%Y-%b-%d"))
    log_filename = date_str + ".csv"
    log_directory = os.path.join(base_directory, ip_address)
    log_directory = os.path.join(log_directory, inverter_addr)
    log_directory = os.path.join(log_directory, string)
    ap.write_log(log_directory, log_filename, header_line, line, debug, True, log_directory, "latest.csv")

    return True

def return_status(status_bin):
    """Convert a binary bitmask to a status string"""
    status_str = ""
    if status_bin & 16:
        status_str += "short circuit"
    if status_bin & 32:
        status_str += " not connected"
    if status_bin & 64:
        status_str += " comms error"
    if status_bin & 128:
        status_str += " disabled"

    return status_str

def read_string(ip_address, port, rtu_address, string_count, write_log_entry, output_directory, debug):
    """Get the string data"""
    # initialise stdout and stderr to NULL
    stdout = ""
    stderr = ""
    register_dict = {}

    # These commands are used to get the parameters from the string monitor.
    # Example: modpoll -a 1 -r 1 -c 87 -1 -p 502 192.168.1.120
    ps = Popen(['modpoll', '-a', rtu_address, '-r', START_REG, '-c', REGS_TO_READ, '-1', '-p', port, ip_address], stdout=PIPE, stderr=PIPE)
    stdout, stderr = ps.communicate()

    # Modpoll will send the data to stderr, but also send errors on stderr as well. weird.
    if debug >= 2:
        print("STDOUT: ", stdout)
        print("STDERR: ", stderr)

    returncode = ps.returncode
    if returncode != 0:
        if debug >= 2:
            print("Bad return value from modpoll: ", returncode)
        return False


    try:
        # for each line, split the register and return values
        for line in stdout.splitlines():
            # if the line starts with a '[', then process it
            # also, convert the key to an INT
            if line.startswith('['):
                line = line.replace('[', '')
                line = line.replace(']', '')
                register, value = line.split(':')
                register = register.strip()
                register_int, result = ap.convert_to_int(register)
                if result:
                    value = value.strip()
                    register_dict[register_int] = value
                else:
                    if debug >= 2:
                        print("Error converting the registers to INTs")
                    return False
    except:
        if debug >= 2:
            print("Error retrieving modbus registers")
        return False


    # The string data is in blocks of 11 registers which repeat up to 8 times

    for string in range(0, string_count):

        offset = string * 11
        idc_string1 = idc_string2 = idc_string3 = idc_string4 = idc_string5 = idc_string6 = idc_string7 = idc_string8 = ""
        temp = status = vdc = ""

        count = 0
        # Get Parameters. If there are 0 parameters, then report an error
        # Otherwise accept the line
        if 1 + offset in register_dict:
            raw = register_dict[1 + offset]
            status_bin, result = ap.convert_to_int(raw)
            if result:
                status = return_status(status_bin)
                count += 1
        if 2 + offset in register_dict:
            raw = register_dict[2 + offset]
            idc1, result = ap.convert_to_float(raw)
            if result:
                idc_string1 = str(idc1 / 100)
                count += 1
        if 3 + offset in register_dict:
            raw = register_dict[3 + offset]
            idc2, result = ap.convert_to_float(raw)
            if result:
                idc_string2 = str(idc2 / 100)
                count += 1
        if 4 + offset in register_dict:
            raw = register_dict[4 + offset]
            idc3, result = ap.convert_to_float(raw)
            if result:
                idc_string3 = str(idc3 / 100)
                count += 1
        if 5 + offset in register_dict:
            raw = register_dict[5 + offset]
            idc4, result = ap.convert_to_float(raw)
            if result:
                idc_string4 = str(idc4 / 100)
                count += 1
        if 6 + offset in register_dict:
            raw = register_dict[6 + offset]
            idc5, result = ap.convert_to_float(raw)
            if result:
                idc_string5 = str(idc5 / 100)
                count += 1
        if 7 + offset in register_dict:
            raw = register_dict[7 + offset]
            idc6, result = ap.convert_to_float(raw)
            if result:
                idc_string6 = str(idc6 / 100)
                count += 1
        if 8 + offset in register_dict:
            raw = register_dict[8 + offset]
            idc7, result = ap.convert_to_float(raw)
            if result:
                idc_string7 = str(idc7 / 100)
                count += 1
        if 9 + offset in register_dict:
            raw = register_dict[9 + offset]
            idc8, result = ap.convert_to_float(raw)
            if result:
                idc_string8 = str(idc8 / 100)
                count += 1
        if 10 + offset in register_dict:
            temp = register_dict[10 + offset]
            count += 1
        if 11 + offset in register_dict:
            vdc = register_dict[11 + offset]
            count += 1

        if count > 1:
            if debug > 0:
                print("For string combiner at IP address: " + ip_address + " and RTU Address: " + rtu_address + " And string: ", (string + 1))
                print("\tInverter Temperature (C): ", temp)
                print("\tStatus: ", status)
                print("\tString Current 1 (A): ", idc_string1)
                print("\tString Current 2 (A): ", idc_string2)
                print("\tString Current 3 (A): ", idc_string3)
                print("\tString Current 4 (A): ", idc_string4)
                print("\tString Current 5 (A): ", idc_string5)
                print("\tString Current 6 (A): ", idc_string6)
                print("\tString Current 7 (A): ", idc_string7)
                print("\tString Current 8 (A): ", idc_string8)
                print("\tString Voltage (V): ", vdc)

            datetime_str = ap.get_datetime_str()

            header = "# Datetime, String Current 1 (A), String Current 2 (A), String Current 3 (A), String Current 4 (A), String Current 5 (A), String Current 6 (A), String Current 7  (A),String Current 8 (A), Temperature (C), Voltage (V), Status\n"

            output_str = datetime_str + "," +  str(idc_string1) + "," + str(idc_string2) + "," + str(idc_string3) + \
                         "," + str(idc_string4) + "," + str(idc_string5) + "," + str(idc_string6) + "," + \
                         str(idc_string7) + "," + str(idc_string8) + "," + str(temp) + "," + str(vdc) + "," + str(status) + "\n"

            if write_log_entry:
                write_line(output_str, ip_address, str(rtu_address), str(string + 1), output_directory, header, debug)

        else:
            if debug > 0:
                print("Could not read values fro string: ", string)

    return True


class Config(object):
    """Config object for click"""
    def __init__(self):
        self.verbosity = 0


CONFIG = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('-v', '--verbose', count=True)
@CONFIG
def cli(config, verbose):
    """Command line entry point"""
    config.verbosity = verbose


@cli.command()
@click.argument('ip_address')
@click.argument('port')
@click.argument('bus_addresses')
@click.argument('strings')
@CONFIG
def discover(config, ip_address, bus_addresses, strings, port):
    """Connect to the target IP address and log the string output for the given bus addresses
       Do not write a log entry"""

    start_time = time.time()

    # Make sure its at least debug level 1
    if config.verbosity == 0:
        config.verbosity = 1

    # convert string_count
    string_count, result = ap.convert_to_int(strings)
    if not result:
        print("Strings must be an integer")
        sys.exit(2)

    for string_addr in ap.parse_address_list(bus_addresses):
        attempts = 3
        while attempts > 0:
            # Try 3 times to make sure a successfull read
            retval = read_string(ip_address, port, str(string_addr), string_count, False, "", config.verbosity)
            if retval:
                # break
                break
            time.sleep(0.1) # ... wait between reads
            attempts -= 1

    elapsed_time = time.time() - start_time
    if config.verbosity > 0:
        print("This request took: ", elapsed_time, " seconds.")

    pass


@cli.command()
@click.argument('ip_address')
@click.argument('port')
@click.argument('bus_addresses')
@click.argument('output_directory')
@click.argument('strings')
@CONFIG
def get(config, ip_address, bus_addresses, output_directory, strings, port):
    """Connect to the target IP address and log the string output for the given bus addresses"""
    # If the logging directory doesn't exist, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    start_time = time.time()

    # convert string_count
    string_count, result = ap.convert_to_int(strings)
    if not result:
        print("Strings must be an integer")
        sys.exit(2)

    for string_addr in ap.parse_address_list(bus_addresses):
        attempts = 3
        while attempts > 0:
            # Try 3 times to make sure a successfull read
            retval = read_string(ip_address, port, str(string_addr), string_count, True, output_directory, config.verbosity)
            if retval:
                # break
                break
            time.sleep(0.1) # ... wait between reads
            attempts -= 1

    elapsed_time = time.time() - start_time
    if config.verbosity > 0:
        print("This request took: ", elapsed_time, " seconds.")


