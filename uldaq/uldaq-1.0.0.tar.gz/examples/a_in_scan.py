#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Wrapper call demonstrated:        ai_device.a_in_scan()
    
    Purpose:                          Performs a continuous scan of the range
                                      of A/D input channels
    
    Demonstration:                    Displays the analog input data for the
                                      range of user-specified channels using
                                      the first supported range and input mode
                                      
    Steps:
    1. Call get_daq_device_inventory() to get the list of available DAQ devices
    2. Create a DaqDevice object
    3. Call daq_device.get_ai_device() to get the ai_device object for the AI subsystem
    4. Verify the ai_device object is valid
    5. Call ai_device.get_info() to get the ai_info object for the AI subsystem
    6. Verify the analog input subsystem has a hardware pacer
    7. Call daq_device.connect() to establish a UL connection to the DAQ device
    8. Call ai_device.a_in_scan() to start the scan of A/D input channels
    9. Call ai_device.get_scan_status() to check the status of the background operation
    10. Display the data for each channel
    11. Call ai_device.scan_stop() to stop the background operation
    12. Call daq_device.disconnect() and daq_device.release() before exiting the process.
"""
from __future__ import print_function
from time import sleep
from os import system
from sys import stdout

from uldaq import get_daq_device_inventory, DaqDevice, AInScanFlag, ScanStatus, ScanOption
from uldaq import create_float_buffer, InterfaceType, AiInputMode


def main():
    daq_device = None
    ai_device = None
    status = ScanStatus.IDLE

    descriptor_index = 0
    range_index = 0
    interface_type = InterfaceType.USB
    low_channel = 0
    high_channel = 3
    samples_per_channel = 10000
    rate = 1000
    scan_options = ScanOption.CONTINUOUS
    flags = AInScanFlag.DEFAULT

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

        # Get the AiDevice object and verify that it is valid.
        ai_device = daq_device.get_ai_device()
        if ai_device is None:
            raise Exception('Error: The DAQ device does not support analog input')

        # Verify that the specified device supports hardware pacing for analog input.
        ai_info = ai_device.get_info()
        if not ai_info.has_pacer():
            raise Exception('\nError: The specified DAQ device does not support hardware paced analog input')

        # Establish a connection to the DAQ device.
        descriptor = daq_device.get_descriptor()
        print('\nConnecting to', descriptor.dev_string, '- please wait...')
        daq_device.connect()

        # Use the SINGLE_ENDED input mode to get the number of channels.
        # If the number of channels is greater than zero, then the device
        # supports the SINGLE_ENDED input mode; otherwise, the device only
        # supports the DIFFERENTIAL input mode.
        number_of_channels = ai_info.get_num_chans_by_mode(AiInputMode.SINGLE_ENDED)
        if number_of_channels > 0:
            input_mode = AiInputMode.SINGLE_ENDED
        else:
            input_mode = AiInputMode.DIFFERENTIAL

        # Verify the high channel does not exceed the number of channels, and
        # set the channel count.
        if high_channel >= number_of_channels:
            high_channel = number_of_channels - 1
        channel_count = high_channel - low_channel + 1

        # Get a list of supported analog input ranges.
        ranges = ai_info.get_ranges(input_mode)
        if range_index >= len(ranges):
            range_index = len(ranges) - 1

        # Allocate a buffer to receive the data.
        data = create_float_buffer(channel_count, samples_per_channel)

        print('\n', descriptor.dev_string, ' ready', sep='')
        print('    Function demonstrated: ai_device.a_in_scan()')
        print('    Channels: ', low_channel, '-', high_channel)
        print('    Input mode: ', input_mode.name)
        print('    Range: ', ranges[range_index].name)
        print('    Samples per channel: ', samples_per_channel)
        print('    Rate: ', rate, 'Hz')
        print('    Scan options:', display_scan_options(scan_options))
        try:
            input('\nHit ENTER to continue\n')
        except (NameError, SyntaxError):
            pass

        system('clear')

        # Start the acquisition.
        rate = ai_device.a_in_scan(low_channel, high_channel, input_mode, ranges[range_index], samples_per_channel,
                                   rate, scan_options, flags, data)

        try:
            while True:
                try:
                    # Get the status of the background operation
                    status, transfer_status = ai_device.get_scan_status()

                    reset_cursor()
                    print('Please enter CTRL + C to terminate the process\n')

                    print('actual scan rate = ', '{:.6f}'.format(rate), 'Hz\n')

                    index = transfer_status.current_index
                    print('currentTotalCount = ',  transfer_status.current_total_count)
                    print('currentScanCount = ',  transfer_status.current_scan_count)
                    print('currentIndex = ',  index, '\n')

                    # Display the data.
                    for i in range(channel_count):
                        clear_eol()
                        print('chan =',
                              i + low_channel, ': ',
                              '{:.6f}'.format(data[index + i]))

                    sleep(0.1)
                except (ValueError, NameError, SyntaxError):
                    break
        except KeyboardInterrupt:
            pass

    except Exception as e:
        print('\n', e)

    finally:
        if daq_device:
            # Stop the acquisition if it is still running.
            if status == ScanStatus.RUNNING:
                ai_device.scan_stop()
            if daq_device.is_connected():
                daq_device.disconnect()
            daq_device.release()


def display_scan_options(bit_mask):
    options = []
    if bit_mask == ScanOption.DEFAULTIO:
        options.append(ScanOption.DEFAULTIO.name)
    for so in ScanOption:
        if so & bit_mask:
            options.append(so.name)
    return ', '.join(options)


def reset_cursor():
    stdout.write('\033[1;1H')


def clear_eol():
    stdout.write('\x1b[2K')


if __name__ == '__main__':
    main()
