"""Turns live Kepware JSON file into simulation server"""
import getopt
import json
import sys
from collections import OrderedDict
from keppy.simulator_device import SimulatorDevice
from keppy.project import Project

DOC = """
Kepware JSON file to Simulation Server converter.

Prints conversion to std-out.

Usage:

    python kepware_real_to_simulation.py [-h]

    python kepware_real_to_simulation.py [-s (8 || 16)] <file-name>

Example: 

    python kepware_real_to_simulation.py -s 16 tags.json > tags-sim.json

Options:

    -h, --help: prints this documentation

    -i, --ignore: file name of a list of tag group names to ignore
    
    -s, --size (optional): Specifies the device register size.
        "8" or "16" for 8 bit or 16 bit. Default is 8 bit.
"""

def process_devices(devices):
    """Process all tags in all devices"""
    for device in devices:
        simulator = SimulatorDevice(device.is_sixteen_bit)
        for tag_group in device.tag_groups:
            for tag in tag_group.tags:
                simulator.process_tag(tag)

def main():
    """MAIN"""
    opts, args = getopt.getopt(
        sys.argv[1: ],
        'h?s:i:',
        [
            'help',
            'size',
            'ignore'])
    is_sixteen_bit = False

    ignore_file = None

    for opt, arg in opts:
        if opt in ('-h', '-?', '--help'):
            print DOC
            sys.exit(0)

        if opt in ('-i', '--ignore'):
            ignore_file = arg

        if opt in ('-s', '--size'):
            is_sixteen_bit = arg == '16'

    if len(args) < 1:
        print """You must at least pass in the filename of the Kepware JSON file.
Use -h for help"""
        sys.exit(1)

    if len(args) > 1:
        print 'Too many arguments passed in. Use -h for help.'
        sys.exit(1)

    with open(args[0]) as f_tags:
        to_ignore = []
        if ignore_file is not None:
            with open(ignore_file) as f_ignore:
                to_ignore = f_ignore.read().split('\n')
        text = f_tags.read()
        # remove first three bytes and encode ascii
        text = text[3:].encode('utf_8')
        kepware_dict = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(text)
        project = Project(kepware_dict, is_sixteen_bit, to_ignore)
        for channel in project.channels:
            channel.set_driver_simulated()
            process_devices(channel.devices)
        project.update()
        print project.as_json()

if __name__ == "__main__":
    main()
