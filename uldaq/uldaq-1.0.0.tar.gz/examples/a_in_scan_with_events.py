#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Wrapper call demonstrated:        daq_device.enable_event() and
                                      ai_device.a_in_scan_wait()
    
    Purpose:                          Use events to determine when data is available
    
    Demonstration:                    Use the a callback function to display the
                                      the data for a user-specified range of
                                      A/D channels
                                      
    Steps:
    1. Call get_daq_device_inventory() to get the list of available DAQ devices
    2. Create a DaqDevice object
    3. Call daq_device.get_ai_device() to get the ai_device object for the AI subsystem
    4. Verify the ai_device object is valid
    5. Call ai_device.get_info() to get the ai_info object for the AI subsystem
    6. Verify the analog input subsystem has a hardware pacer
    7. Call daq_device.connect() to establish a UL connection to the DAQ device
    8. Initialize the ScanEventParameters structure used to pass parameters to the callback function
    9. Call daq_device.enable_event to enable the DE_ON_DATA_AVAILABLE event
    10. Call ai_device.a_in_scan() to start a finite scan of the A/D channels
    11. Call ai_device.a_in_scan_wait() to wait for the finite scan to complete
    12. The callback is called each time 100 samples are available to allow the data to be displayed
    13. Call ai_device.scan_stop() to stop the background operation
    14. Call daq_device.disconnect() and daq_device.release() before exiting the process.
"""
from __future__ import print_function
from os import system
from sys import stdout
from collections import namedtuple

from uldaq import get_daq_device_inventory, DaqDevice, AInScanFlag, DaqEventType, WaitType, ScanOption
from uldaq import InterfaceType, AiInputMode, create_float_buffer, ULException, EventCallbackArgs


def main():
    global rate
    daq_device = None
    ai_device = None

    descriptor_index = 0
    range_index = 0
    interface_type = InterfaceType.USB
    low_channel = 0
    high_channel = 3
    samples_per_channel = 10000
    rate = 1000
    flags = AInScanFlag.DEFAULT
    event_types = DaqEventType.ON_DATA_AVAILABLE | DaqEventType.ON_END_OF_INPUT_SCAN | DaqEventType.ON_INPUT_SCAN_ERROR

    ScanParams = namedtuple('ScanParams', 'buffer high_chan low_chan')

    # set the scan options for a FINITE scan ... to set the scan options for
    # a continuous scan, uncomment the line that or's the SO_CONTINUOUS option
    # into to the scanOptions variable
    #
    # if this is changed to a CONTINUOUS scan, then changes will need to be made
    # to the event handler (event_callback_function) to account for the buffer wrap
    # around condition
    scan_options = ScanOption.DEFAULTIO
    # scan_options |= ScanOption.CONTINUOUS

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

        # Store the scan event parameters for use in the callback function.
        scan_event_parameters = ScanParams(data, high_channel, low_channel)

        # Enable the event to be notified every time 100 samples are available.
        available_sample_count = 100
        daq_device.enable_event(event_types, available_sample_count, event_callback_function,
                                scan_event_parameters)

        print('\n', descriptor.dev_string, 'ready', sep='')
        print('    Function demonstrated: daq_device.enable_event()')
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

        # Start the finite acquisition.
        rate = ai_device.a_in_scan(low_channel, high_channel, input_mode, ranges[range_index], samples_per_channel,
                                   rate, scan_options, flags, data)

        # Wait here until the scan is done ... events will be handled in the event handler
        # (eventCallbackFunction) until the background scan completes
        time_to_wait = -1.0
        ai_device.scan_wait(WaitType.WAIT_UNTIL_DONE, time_to_wait)

    except KeyboardInterrupt:
        pass
    except (ValueError, NameError, SyntaxError):
        pass
    except Exception as e:
        print('\n', e)
    finally:
        if daq_device:
            # Stop the acquisition if it is still running.
            if ai_device:
                ai_device.scan_stop()
            daq_device.disable_event(event_types)
            if daq_device.is_connected():
                daq_device.disconnect()
            daq_device.release()


def event_callback_function(event_callback_args):
    # type: (EventCallbackArgs) -> None
    """
    The callback function called in response to an event condition.

    Args:
        event_callback_args: Named tuple :class:`EventCallbackArgs` used to pass
            parameters to the user defined event callback function :class`DaqEventCallback`.
            The named tuple contains the following members
            event_type - the condition that triggered the event
            event_data - additional data that specifies an event condition
            user_data - user specified data that will be passed to the callback function
    """

    event_type = event_callback_args.event_type
    event_data = event_callback_args.event_data
    user_data = event_callback_args.user_data

    if event_type == DaqEventType.ON_DATA_AVAILABLE or event_type == DaqEventType.ON_END_OF_INPUT_SCAN:
        reset_cursor()
        print('eventType: ', DaqEventType(event_type).name)

        scan_event_parameters = user_data
        total_samples = event_data
        chan_count = scan_event_parameters.high_chan - scan_event_parameters.low_chan + 1

        print('eventData: ', total_samples, '\n')

        print('actual scan rate = ', '{:.6f}'.format(rate), 'Hz\n')

        # If this example is changed to a CONTINUOUS scan, then you will need
        # to maintain the index of where the data is being written to the buffer
        # to handle the buffer wrap around condition.
        index = (total_samples * chan_count) - chan_count
        print('currentIndex = ', index, '\n')

        for i in range(chan_count):
            print('chan =',
                  i + scan_event_parameters.low_chan,
                  '{:.6f}'.format(scan_event_parameters.buffer[index + i]))

    if event_type == DaqEventType.ON_INPUT_SCAN_ERROR:
        exception = ULException(event_data)
        print(exception)

    if event_type == DaqEventType.ON_END_OF_INPUT_SCAN:
        print('\nThe scan is complete\n')


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


if __name__ == '__main__':
    main()
