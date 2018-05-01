#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    UL call demonstrated:             CtrDevice.c_in()

    Purpose:                          Reads a counter input channel

    Demonstration:                    Displays the event counter input data
                                      on a user-specified channel

    Steps:
    1. Call get_daq_device_inventory() to get the list of available DAQ devices
    2. Call DaqDevice() to create a DaqDevice object
    3. Call DaqDevice.get_ctr_device() to get the CtrDevice object for the counter subsystem
    4. Verify the CtrDevice object is valid
    5. Call DaqDevice.connect() to connect to the device
    6. Call CtrDevice.c_clear() to clear the counter (set it to 0)
    7. Call CtrDevice.c_in() to read a value from the counter channel
    8. Call DaqDevice.disconnect() and DaqDevice.release() before exiting the process
"""
from __future__ import print_function
from time import sleep
from sys import stdout
from os import system

from uldaq import get_daq_device_inventory, DaqDevice, InterfaceType


def main():
    counter_number = 0
    interface_type = InterfaceType.USB
    daq_device = None

    try:
        # Get descriptors for all of the available DAQ devices.
        devices = get_daq_device_inventory(interface_type)
        number_of_devices = len(devices)

        # Verify at least one DAQ device is detected.
        if number_of_devices == 0:
            raise Exception('Error: No DAQ devices found')

        print('Found', number_of_devices, 'DAQ device(s):')
        for i in range(number_of_devices):
            print('    ', devices[i].product_name, ' (', devices[i].unique_id, ')', sep='')

        # Create a DaqDevice object from the first descriptor.
        daq_device = DaqDevice(devices[0])
        ctr_device = daq_device.get_ctr_device()

        # Verify the specified DAQ device supports counters.
        if ctr_device is None:
            raise Exception('Error: The DAQ device does not support counters')

        descriptor = daq_device.get_descriptor()
        print('\nConnecting to', descriptor.dev_string, '- please wait...')
        # Establish a connection to the device.
        daq_device.connect()

        ctr_info = ctr_device.get_info()
        dev_num_counters = ctr_info.get_num_ctrs()
        if counter_number >= dev_num_counters:
            counter_number = dev_num_counters - 1

        print('\n', descriptor.dev_string, 'ready')
        print('    Function demonstrated: CtrDevice.c_in')
        print('    Counter:', counter_number)
        try:
            input('\nHit ENTER to continue')
        except (NameError, SyntaxError):
            pass

        system('clear')
        print('\n*Press Ctrl-C to stop')

        ctr_device.c_clear(counter_number)
        try:
            while True:
                try:
                    # Read and display the data.
                    counter_value = ctr_device.c_in(counter_number)
                    print('\r    Counter ', counter_number, ':', str(counter_value).rjust(12), sep='', end='')
                    stdout.flush()
                    sleep(0.1)
                except (ValueError, NameError, SyntaxError):
                    break
        except KeyboardInterrupt:
            pass

    except Exception as e:
        print('\n', e)

    finally:
        if daq_device:
            # Disconnect from the DAQ device.
            if daq_device.is_connected():
                daq_device.disconnect()
            # Release the DAQ device resource.
            daq_device.release()


if __name__ == '__main__':
    main()
