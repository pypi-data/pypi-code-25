"""
- This script can query many ethernet connected VSN800 weather stations.
- To discover RS485 address range and print out the station metadata
```
Usage: vsn800_ardexa discover ip_address port rs485_addresses
Eg; vsn800_ardexa discover 192.168.1.2 502 10-20
```

Send production data to a file on disk 
```
Usage: vsn800_ardexa get ip_address port rs485_addresses log_directory
Eg; vsn800_ardexa get 192.168.1.2 502 14-21 /opt/ardexa
```
{IP Address} = IP address of the weather stations combiner, eg; 192.168.1.2
{Port} = Modbus port, eg; 502
{RS485 Address(es)} = RS485 address or range of addresses, eg; 1-5 or 1,2,3 or 4 (for example)
{log directory} = logging directory, eg; /opt/ardexa/

To view debug output, increase the verbosity using the `-v` flag.
- standard (no messages, except errors), `-v` (discovery messages) or `-vv` (all messages)

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
REGS_TO_READ = "125"


def write_line(line, ip_address, inverter_addr, base_directory, header_line, debug):
    """This will write a line to the base_directory
    Assume header and lines are already \n terminated"""
    # Write the log entry, as a date entry in the log directory
    date_str = (time.strftime("%Y-%b-%d"))
    log_filename = date_str + ".csv"
    log_directory = os.path.join(base_directory, ip_address)
    log_directory = os.path.join(log_directory, inverter_addr)
    ap.write_log(log_directory, log_filename, header_line, line, debug, True, log_directory, "latest.csv")

    return True



def read_weather(ip_address, port, rtu_address, write_log_entry, output_directory, debug):
    """Get the weather data"""
    # initialise stdout and stderr to NULL
    stdout = ""
    stderr = ""
    register_dict = {}

    # These commands are used to get the parameters from the string monitor.
    # Example: modpoll -a 3 -r 1 -c 125 -1 -p 502 192.168.1.10
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
                value = value.strip()
                register_dict[register] = value
    except:
        if debug >= 2:
            print("Error retrieving modbus registers")
        return False


    temp = panel_temp = horiz_radiation = plane_radiation = ""

    count = 0
    # Get Parameters. If there are 0 parameters, then report an error
    # Otherwise accept the line
    if "72" in register_dict:
        raw = register_dict["72"]
        temp_fl, result = ap.convert_to_float(raw)
        if result:
            temp = str(temp_fl / 10)
            count += 1

    if "85" in register_dict:
        horiz_radiation = register_dict["85"]
        count += 1

    if "86" in register_dict:
        plane_radiation = register_dict["86"]
        count += 1

    if "92" in register_dict:
        raw = register_dict["92"]
        panel_temp_fl, result = ap.convert_to_float(raw)
        if result:
            panel_temp = str(panel_temp_fl / 10)
            count += 1

    if count > 1:
        if debug > 0:
            print("For ABB VSN800 Weather station at IP address: " + ip_address + " and RTU Address: " + rtu_address)
            print("\tAmbient Outside Temperature (C): ", temp)
            print("\tPanel Temperature (C): ", panel_temp)
            print("\tGobal Horizontal Radiation (W/m^2): ", horiz_radiation)
            print("\tPlane Radiation (W/m^2): ", plane_radiation)

        datetime_str = ap.get_datetime_str()

        header = "# Datetime, Ambient Temperature (C), Panel Temp (C), Global Horiz Radiation (W/m^2), Plane Radiation (W/m^2)\n"

        output_str = datetime_str + "," +  str(temp) + "," + str(panel_temp) + "," + str(horiz_radiation) + "," + str(plane_radiation) + "\n"

        if write_log_entry:
            write_line(output_str, ip_address, str(rtu_address), output_directory, header, debug)

    else:
        if debug > 0:
            print("Could not read values from the weather station")
        return False

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
@CONFIG
def discover(config, ip_address, bus_addresses, port):
    """Connect to the target IP address and log the weather station output for the given bus addresses
       Do not write a log entry"""

    start_time = time.time()

    # Make sure its at least debug level 1
    if config.verbosity == 0:
        config.verbosity = 1

    for weather_addr in ap.parse_address_list(bus_addresses):
        attempts = 3
        while attempts > 0:
            # Try 3 times to make sure a successfull read
            retval = read_weather(ip_address, port, str(weather_addr), False, "", config.verbosity)
            if retval:
                # break
                break
            time.sleep(0.1) # ... wait between reads
            attempts -= 1

    elapsed_time = time.time() - start_time
    if config.verbosity > 0:
        print("This request took: ", elapsed_time, " seconds.")


@cli.command()
@click.argument('ip_address')
@click.argument('port')
@click.argument('bus_addresses')
@click.argument('output_directory')
@CONFIG
def get(config, ip_address, bus_addresses, output_directory, port):
    """Connect to the target IP address and log the weather station output for the given bus addresses"""
    # If the logging directory doesn't exist, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    start_time = time.time()


    for weather_addr in ap.parse_address_list(bus_addresses):
        attempts = 3
        while attempts > 0:
            # Try 3 times to make sure a successfull read
            retval = read_weather(ip_address, port, str(weather_addr), True, output_directory, config.verbosity)
            if retval:
                # break
                break
            time.sleep(0.1) # ... wait between reads
            attempts -= 1

    elapsed_time = time.time() - start_time
    if config.verbosity > 0:
        print("This request took: ", elapsed_time, " seconds.")


