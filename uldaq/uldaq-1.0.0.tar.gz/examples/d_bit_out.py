#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Wrapper call demonstrated:        dio_device.d_bit_out()

    Purpose:                          Writes a value to each of the bits for
                                      the specified DIO port

    Demonstration:                    Writes the value of each bit in the
                                      digital port
    Steps:
    1. Call get_daq_device_inventory() to get the list of available DAQ devices
    2. Create a DaqDevice object
    3. Call daq_device.get_info() to get the daq_device_info object for the DAQ device
    4. Verify that the DAQ device has a digital output subsystem
    5. Call daq_device.connect() to establish a UL connection to the DAQ device
    6. Call daq_device.get_dio_device() to get the dio_device object for the digital subsystem
    7. Call dio_device.d_bit_out() to read each bit of the digital port
    8. Display the data for each bit
"""
from __future__ import print_function
from time import sleep
from os import system
from sys import stdout

from uldaq import get_daq_device_inventory, DaqDevice, InterfaceType, DigitalDirection, DigitalPortIoType


def main():
    daq_device = None
    dio_device = None
    port_to_write = None

    interface_type = InterfaceType.USB
    descriptor_index = 0
    port_types_index = 0

    try:
        # Get descriptors for all of the available DAQ devices.
        devices = get_daq_device_inventory(interface_type)
        number_of_devices = len(devices)
        if number_of_devices == 0:
            raise Exception('Error: No DAQ devices found')

        print('Found', number_of_devices, 'DAQ device(s):')
        for i in range(number_of_devices):
            print('  ', devices[i].product_name, ' (', devices[i].unique_id, ')', sep='')

        # Create the DAQ device object associated with the specified descriptor index.
        daq_device = DaqDevice(devices[descriptor_index])

        # Get the DioDevice object and verify that it is valid.
        dio_device = daq_device.get_dio_device()
        if dio_device is None:
            raise Exception('Error: The device does not support digital output')

        # Establish a connection to the DAQ device.
        descriptor = daq_device.get_descriptor()
        print('\nConnecting to', descriptor.dev_string, '- please wait...')
        daq_device.connect()

        # Get the port types for the device(AUXPORT, FIRSTPORTA, ...)
        dio_info = dio_device.get_info()
        port_types = dio_info.get_port_types()

        if port_types_index >= len(port_types):
            port_types_index = len(port_types) - 1

        port_to_write = port_types[port_types_index]

        # Get the port I/O type and the number of bits for the first port.
        port_info = dio_info.get_port_info(port_to_write)

        # If the port is bit configurable, then configure the individual bits
        # for output; otherwise, configure the entire port for output.
        if port_info.port_io_type == DigitalPortIoType.BITIO:
            # Configure all of the bits for output for the first port.
            for bit_number in range(port_info.number_of_bits):
                dio_device.d_config_bit(port_to_write, bit_number, DigitalDirection.OUTPUT)
        else:
            # Configure the entire port for output.
            dio_device.d_config_port(port_to_write, DigitalDirection.OUTPUT)

        max_port_value = pow(2.0, port_info.number_of_bits) - 1

        print('\n', descriptor.dev_string, ' ready', sep='')
        print('    Function demonstrated: dio_device.d_bit_out()')
        print('    Port: ', port_to_write.name)
        print('    Port I/O type: ', port_info.port_io_type.name)
        print('    Bits: ', port_info.number_of_bits)
        try:
            input('\nHit ENTER to continue\n')
        except (NameError, SyntaxError):
            pass

        system('clear')

        try:
            while True:
                try:
                    reset_cursor()
                    print('Enter a value  between 0 and ', max_port_value, ' (or non-numeric character to exit):  ')
                    clear_eol()
                    data = input()

                    for bit_number in range(port_info.number_of_bits):
                        bit_value = (int(data) >> bit_number) & 1
                        dio_device.d_bit_out(port_to_write, bit_number, bit_value)

                        print('Bit(', bit_number, ') Data: ', bit_value)

                    sleep(0.1)
                except (ValueError, NameError, SyntaxError):
                    break
        except KeyboardInterrupt:
            pass

    except Exception as e:
        print('\n', e)

    finally:
        if daq_device:
            if dio_device and port_to_write is not None:
                # before disconnecting, set the port back to input
                dio_device.d_config_port(port_to_write, DigitalDirection.INPUT)
            if daq_device.is_connected():
                daq_device.disconnect()
            daq_device.release()


def reset_cursor():
    stdout.write('\033[1;1H')


def clear_eol():
    stdout.write('\x1b[2K')


if __name__ == '__main__':
    main()
